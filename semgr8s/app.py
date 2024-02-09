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

APP = Flask(__name__)
DATA_FOLDER = "/app/data"


@APP.route("/health", methods=["GET", "POST"])
def healthz():
    """
    Handle the '/health' endpoint and check the health status of the web server.
    Return '200' status code.
    """
    return "", 200


@APP.route("/ready", methods=["GET"])
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
    """
    uid = ""

    try:
        req = (request.json).get("request", {})
        APP.logger.debug("+ request: %s", req)

        if not req:
            return send_response(
                False, "none", "Invalid request, no payload.request found"
            )

        uid = req.get("uid", "")
        if not uid:
            return send_response(
                False, "none", "Invalid request, no payload.request.uid found"
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
            APP.logger.debug("+ semgrep exit: %s", err)

        with open(results_file, "r", encoding="utf-8") as file:
            results = json.load(file)
        APP.logger.debug("+ scan results: %s", results)

        if results["errors"]:
            APP.logger.error("ERROR: %s", results["errors"])
            return send_response(True, uid, "Request caused error during scan")

        if results["results"]:
            num_findings = len(results["results"])
            findings = "\n" + "\n".join(
                ["* " + f["check_id"] for f in results["results"]]
            )
            APP.logger.debug("+ %s findings: %s", num_findings, findings)
            return send_response(
                False,
                uid,
                f"Found {num_findings} violation(s) of the following policies: {findings}",
            )
    except Exception as err:  # pylint: disable=W0718
        return send_response(False, uid, f"Webhook exception: {err}")
    finally:
        try:
            os.remove(results_file)
            os.remove(k8s_yaml_file)
        except FileNotFoundError:
            pass

    return send_response(True, uid, "Request has required labels")


def send_response(allowed, uid, message):
    """
    Prepare json response in expected format based on validation result.
    """
    APP.logger.debug(
        "> response:(allowed=%s, uid=%s, message=%s)", allowed, uid, message
    )
    return jsonify(
        {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "allowed": allowed,
                "uid": uid,
                "status": {"message": message},
            },
        }
    )
