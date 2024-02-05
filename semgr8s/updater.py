"""
Update cached rules from configmaps.
"""

import logging
import os

from urllib.parse import urlencode

from semgr8s.k8s_api import request_kube_api


def update_rules():
    """
    Request all rule configmaps from kubernetes api and store locally in semgrep format.
    """
    logging.info("updateing rule set")

    try:
        namespace = os.environ.get("NAMESPACE", "default")
        query = {"labelSelector": "semgr8s/rule"}

        rules = request_kube_api(
            f"api/v1/namespaces/{namespace}/configmaps?{urlencode(query)}"
        )

        for rule in rules["items"]:
            file, content = list(rule["data"].items())[0]

            logging.debug("updating %s rule", file)
            with open(f"/app/rules/{file}", "w", encoding="utf-8") as rule_file:
                rule_file.write(content)
    except Exception as err:  # pylint: disable=W0718
        logging.error("Error updating rules: %s", err)
