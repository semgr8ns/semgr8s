import logging
import os
import pytest

import semgr8s.updater as supdater

from . import conftest as fix


# BE CAREFUL files created in previous runs, remain accessible
@pytest.mark.parametrize(
    "namespace, created_files, logtext",
    [
        (
            "default",
            ["tester-test-name.yaml"],
            "",
        ),
        (
            "semgr8ns",
            ["tester-test-name1.yaml"],
            "",
        ),
        (
            "broken_nodata",
            ["tester-test-broken.yaml"],
            "",
        ),
        (
            "multiplerulesinmap",
            [
                "tester-test-multiplerules1.yaml",
                "tester-test-multiplerules2.yaml",
            ],
            "",
        ),
    ],
)
def test_updater(monkeypatch, caplog, m_request, namespace, created_files, logtext):
    monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "127.0.0.1")
    monkeypatch.setenv("KUBERNETES_SERVICE_PORT", "1234")
    monkeypatch.setenv("NAMESPACE", namespace)
    supdater.update_rules()
    for f in created_files:
        assert f"{f}" in os.listdir("/app/rules/")
        assert logtext in caplog.text
