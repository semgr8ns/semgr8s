"""
Flask application to expose required paths and generate suitable responses.
"""

import json
import os
import sys

import yaml
from flask import Flask, jsonify, request
from semgrep.cli import cli
from werkzeug.utils import secure_filename
from werkzeug.exceptions import UnsupportedMediaType

APP = Flask(__name__)
DATA_FOLDER = "/app/data"


@APP.route("/health", methods=["GET", "POST"])
def healthz():
    """
    Handle the '/health' endpoint and check the health status of the web server.
    Return '200' status code.
    """
    return "", 200


@APP.route("/ready", methods=["GET", "POST"])
def readyz():
    """
    Handle the '/ready' endpoint and check the readiness of the web server.
    Return '200' status code.
    """
    return "", 200


@APP.route("/validate", methods=["POST"])
def validate():
    """
    Handle the '/validate' endpoint and accept admission rquests.
    Return response allowing or denying the request.

    Return '200' status code with response:
    {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'allowed': <bool True/False>,
            'status': {
                'code': <int http_status_codes>,
                'message': <str reponse_message>
            },
            'uid': <str admission_request_uid>
        }
    }

    Response payload status codes:
    * 201 - Admitted
    * 400 - Malformed request payload lacking 'request' key/values
    * 403 - Request violates policy rules
    * 415 - Unsupported request payload media type
    * 418 - Error during semgrep scan
    * 422 - Malformed request payload without 'request.uid' key
    * 500 - Unexpected Webhook exception

    """
    uid = ""

    try:
        APP.logger.debug("+ request object: %s", request)
        try:
            req = (request.json).get("request", {})
        except (UnsupportedMediaType, AttributeError) as err:
            return send_response(False, "none", 415, f"Unsupported Media Type: {err}")

        APP.logger.debug("+ request: %s", req)

        if not req:
            return send_response(
                False, "none", 400, "Malformed request, no payload.request found"
            )

        uid = req.get("uid", "")
        if not uid:
            return send_response(
                False, "none", 422, "Malformed request, no payload.request.uid found"
            )
        k8s_yaml_file = os.path.join(DATA_FOLDER, secure_filename(f"k8s_{uid}.yml"))
        results_file = os.path.join(DATA_FOLDER, secure_filename(f"results_{uid}.json"))

        k8syaml = req.get("object", {})
        with open(k8s_yaml_file, "w", encoding="utf-8") as file:
            yaml.dump(k8syaml, file, default_flow_style=False)

        remote_rules = []
        for remote_rule in os.environ.get("SEMGREP_RULES", "").split(" "):
            if remote_rule:
                remote_rules += ["--config", remote_rule]

        sys.argv = [
            "scan",
            "--metrics",
            "off",
            "--disable-version-check",
            "--config",
            "/app/rules/",
            *remote_rules,
            "--json",
            "--output",
            results_file,
            k8s_yaml_file,
        ]

        APP.logger.debug("+ sys.argv: %s", sys.argv)

        try:
            cli()  # pylint: disable=no-value-for-parameter
        except SystemExit as err:
            APP.logger.info("+ Unexpected semgrep error recorded: %s", err)

        with open(results_file, "r", encoding="utf-8") as file:
            results = json.load(file)
        APP.logger.debug("+ scan results: %s", results)

        if results["errors"]:
            APP.logger.error("ERROR: %s", results["errors"])
            return send_response(False, uid, 418, "Request caused error during semgrep scan")

        if results["results"]:
            num_findings = len(results["results"])
            findings = "\n" + "\n".join(
                ["* " + f["check_id"] for f in results["results"]]
            )
            APP.logger.debug("+ %s finding(s): %s", num_findings, findings)
            return send_response(
                False,
                uid,
                403,
                f"Found {num_findings} violation(s) of the following policies: {findings}",
            )
    except Exception as err:  # pylint: disable=W0718
        return send_response(False, uid, 500, f"Unexpected Webhook exception: {err}")
    finally:
        try:
            os.remove(results_file)
            os.remove(k8s_yaml_file)
        except (FileNotFoundError, UnboundLocalError):
            pass

    return send_response(True, uid, 201, "Compliant resource admitted")


def send_response(allowed, uid, code, message):
    """
    Prepare json response in expected format based on validation result.
    """
    APP.logger.info(
        "> response:(allowed=%s, uid=%s, status_code=%s message=%s)",
        allowed,
        uid,
        code,
        message,
    )
    return jsonify(
        {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "allowed": allowed,
                "uid": uid,
                "status": {"code": code, "message": message},
            },
        }
    )
