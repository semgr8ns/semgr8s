"""
Update cached rules from configmaps.
"""

import os

from urllib.parse import urlencode

from semgr8s.k8s_api import request_kube_api
from semgr8s.app import APP

RULESPATH = "/app/rules"


def update_rules():
    """
    Request all rule configmaps from kubernetes api and store locally in semgrep format.
    """
    APP.logger.debug("Updating rule set")

    try:
        old_rule_files = [
            file
            for file in os.listdir(RULESPATH)
            if os.path.isfile(os.path.join(RULESPATH, file))
        ]
        namespace = os.getenv("NAMESPACE", "default")
        query = {"labelSelector": "semgr8s/rule"}

        rules = request_kube_api(
            f"api/v1/namespaces/{namespace}/configmaps?{urlencode(query)}"
        )

        for item in rules.get("items", []):
            data = list(item.get("data", {}).items())
            for datum in data:
                file, content = datum
                path = os.path.join(RULESPATH, file)
                with open(path, "w", encoding="utf-8") as rule_file:
                    rule_file.write(content)
                APP.logger.debug("Updated %s rule", file)
                try:
                    old_rule_files.remove(file)
                except ValueError:
                    pass
        for deprecated_rule in old_rule_files:
            os.remove(os.path.join(RULESPATH, deprecated_rule))
            APP.logger.info("Deleted %s rule", deprecated_rule)
    except Exception as err:  # pylint: disable=W0718
        APP.logger.error("Updating rules failed unexpectedly: %s", err)
