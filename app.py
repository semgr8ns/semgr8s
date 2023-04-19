import json, logging, os, sys

import yaml

from flask import Flask, jsonify, request
from semgrep.cli import cli

app = Flask('webhook')
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.DEBUG)

#Default route
@app.route("/", methods=['GET'])
def hello():
  return jsonify({"message": "Hello validation controller"})


#Health check
@app.route("/ping", methods=['GET'])
def ping():
  return jsonify({'message': 'pong'})


@app.route('/validate', methods=['POST'])
def deployment_webhook():
  r = request.get_json()

  req = r.get('request', {})
  app.logger.debug(f"+ request: {req}")
  uid = ''
  try:
    if not req:
      return send_response(False, '<no uid>', "Invalid request, no payload.request found")

    uid = req.get("uid", '')
    app.logger.debug(f"+ uid: {uid}")
    if not uid:
      return send_response(False, '<no uid>', "Invalid request, no payload.request.uid found")

    k8syaml = req.get("object", {})
    with open('k8s.yml', 'w') as f:
        yaml.dump(k8syaml, f, default_flow_style=False)

    sys.argv = ['scan', '--config', 'r/yaml.kubernetes', '--json', '--output', 'results.json', 'k8s.yml']
    try:
        cli()
    except SystemExit as e:
        app.logger.debug("+ semgrep exit: %s", e)
    with open('results.json', 'r') as f:
        results = json.load(f)
    app.logger.debug("+ scan results: %s", results)

    if results['errors']:
        app.logger.error("ERROR: %s", results['errors'])
        return send_response(True, uid, "Request caused error during scan")

    if results['results']:
        num_findings = len(results['results'])
        findings = "\n"+'\n'.join(["->"+f['check_id'] for f in results['results']])
        app.logger.debug("+ %s findings: %s", num_findings, findings)
        return send_response(False, uid, f"{num_findings} findings: {findings}")

#    labels = req.get("object", {}).get("metadata", {}).get("labels")
#    app.logger.debug(f"+ labels: {labels}")
#    if 'ngaddons/bypass' in labels:
#      return send_response(True, uid, "Request bypassed as 'ngaddons/bypass' is set")
#
#    missing = [ l for l in REQUIRED_LABELS if l not in labels ]
#    app.logger.debug(f"+ missing: {missing}")
#    if missing:
#      return send_response(False, uid, f"Missing labels: {missing}")

  except Exception as e:
    return send_response(False, uid, f"Webhook exception: {e}")

  #Send OK
  return send_response(True, uid, "Request has required labels")


#Function to respond back to the Admission Controller
def send_response(allowed, uid, message):
  app.logger.debug(f"> response:(allowed={allowed}, uid={uid}, message={message})")
  return jsonify({
      "apiVersion": "admission.k8s.io/v1", 
      "kind": "AdmissionReview",
      "response": {
        "allowed": allowed, 
        "uid": uid,
        "status": {"message": message}
    }
  })


if __name__ == "__main__":
  ca_crt = 'certs/ca.crt' if os.path.isfile('certs/ca.crt') else '/etc/ssl/ca.crt'
  ca_key = 'certs/ca.key' if os.path.isfile('certs/ca.crt') else '/etc/ssl/ca.key'
  app.run(ssl_context=(ca_crt, ca_key), port=5000, host='0.0.0.0', debug=True)
