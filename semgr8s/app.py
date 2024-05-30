"""
Flask application to expose required paths and generate suitable responses.
"""

import base64
import json
import os
import sys

import jsonpatch
from flask import Flask, jsonify, request
from semgrep.cli import cli
from werkzeug.exceptions import UnsupportedMediaType

from semgr8s.files import S8sFiles

APP = Flask(__name__)


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
    Handle the '/validate' endpoint and accept admission requests.
    Return response allowing or denying the request.
    """

    return perform_review(request, autofix=False)


@APP.route("/mutate", methods=["POST"])
def mutate():
    """
    Handle the '/mutate' endpoint and accept admission requests.
    Return response allowing, denying, or modifying the request.
    """

    return perform_review(request, autofix=True)


def perform_review(
    admission_request, autofix=False
):  # pylint: disable=too-many-return-statements,too-many-branches
    """
    Review admission request using semgrep as policy engine.
    Return admission response.

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
    * 202 - Passed mutation phase, validation still open
    * 400 - Malformed request payload lacking 'request' key/values
    * 403 - Request violates policy rules
    * 406 - K8s resource 'event' ignored
    * 415 - Unsupported request payload media type
    * 418 - Error during semgrep scan
    * 422 - Malformed request payload without 'request.uid' key
    * 500 - Unexpected Webhook exception
    """
    uid = ""
    files = S8sFiles()

    try:
        APP.logger.debug("+ request object: %s", admission_request)
        try:
            req = (admission_request.get_json()).get("request", {})
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

        kind = req.get("kind", {}).get("kind", "")
        APP.logger.debug("+ k8s resource kind: %s", kind)
        if not kind or kind == "Event":
            return send_response(True, uid, 406, f"Ignored k8s resource kind '{kind}'")

        k8s_res = req.get("object", {})
        files.write_k8s_yaml(data=k8s_res)

        remote_rules = []
        for remote_rule in os.environ.get("SEMGREP_RULES", "").split(" "):
            if remote_rule:
                remote_rules += ["--config", remote_rule]

        sys.argv = [
            "scan",
            "--metrics",
            "off",
            "--disable-version-check",
            "--disable-nosem",
            *(["--autofix"] if autofix else []),
            "--config",
            "/app/rules/",
            *remote_rules,
            "--json",
            "--output",
            files.results_file,
            files.k8s_yaml_file,
        ]

        APP.logger.debug("+ sys.argv: %s", sys.argv)

        try:
            cli()  # pylint: disable=no-value-for-parameter
        except SystemExit as err:
            APP.logger.info("+ Unexpected semgrep error recorded: %s", err)

        results = files.results
        APP.logger.debug("+ scan results: %s", results)

        if results["errors"]:
            APP.logger.error("ERROR: %s", results["errors"])
            return send_response(
                False, uid, 418, "Request caused error during semgrep scan"
            )

        if results["results"]:
            if autofix:
                patched_k8s_res = files.read_k8s_yaml()
                patches = jsonpatch.JsonPatch.from_diff(k8s_res, patched_k8s_res).patch
            else:
                patches = None
            num_findings = len(results["results"])
            findings = "\n" + "\n".join(
                ["* " + f["check_id"] for f in results["results"]]
            )
            APP.logger.debug("+ %s finding(s): %s", num_findings, findings)
            return send_response(
                autofix,
                uid,
                202 if autofix else 403,
                f"Found {num_findings} violation(s) of the following policies: {findings}",
                patch=patches,
            )
    except Exception as err:  # pylint: disable=W0718
        return send_response(False, uid, 500, f"Unexpected Webhook exception: {err}")
    finally:
        files.remove_files()

    return send_response(True, uid, 201, "Compliant resource admitted")


def send_response(allowed, uid, code, message, patch=None):
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
    review = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "allowed": allowed,
            "uid": uid,
            "status": {"code": code, "message": message},
        },
    }
    if patch:
        review["response"]["patchType"] = "JSONPatch"
        review["response"]["patch"] = base64.b64encode(
            bytearray(json.dumps(patch), "utf-8")
        ).decode("utf-8")

    return jsonify(review)
