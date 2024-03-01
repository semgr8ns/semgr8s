import logging
import pytest

import semgr8s.k8s_api as kapi

from . import conftest as fix


@pytest.mark.parametrize(
    "url, response, logtext",
    [
        (
            "https://samplek8s.io/apis/v1/namespaces/default/pods/sample-pod",
            fix.get_k8s_res("pods"),
            "",
        ),
        (
            "https://samplek8s.io/apis/v1/namespaces/default/deployments/sample-dpl",
            fix.get_k8s_res("deployments"),
            "",
        ),
        (
            "https://samplek8s.io/apis/v1/namespaces/broken_nojson/configmaps/sample-cm",
            {},
            "Malformed k8s API response or resource yaml",
        ),
    ],
)
def test_request_kube_api(
    monkeypatch, caplog, m_request, url: str, response: dict, logtext: str
):
    monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "127.0.0.1")
    monkeypatch.setenv("KUBERNETES_SERVICE_PORT", "1234")
    assert kapi.request_kube_api(url) == response
    assert logtext in caplog.text
