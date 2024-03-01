import json
import pytest
import re
import requests
from contextlib import contextmanager


import semgr8s.k8s_api

"""
This file is used for sharing fixtures across all other test files.
https://docs.pytest.org/en/stable/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session
"""


@contextmanager
def no_exc():
    yield


def get_json(path):
    with open(path, "r") as file:
        return json.load(file)


def get_admreq(adm_type):
    try:
        return get_json(
            f"tests/data/sample_admission_requests/admission_request_{adm_type}.json"
        )
    except FileNotFoundError:
        return None


@pytest.fixture
def adm_req_samples():
    return [
        get_admreq(t)
        for t in (
            "empty",
            "no_request",
            "no_request_uid",
            "deployments",
            "deployments_forbiddenlabel",
            "pods",
            "pods_forbiddenlabel",
        )
    ]


def get_k8s_res(path, namespace="default"):
    if namespace == "default":
        return get_json(f"tests/data/sample_k8s_resources/{path}.json")
    else:
        return get_json(f"tests/data/sample_k8s_resources/{path}_{namespace}.json")


@pytest.fixture
def m_request(monkeypatch):
    monkeypatch.setattr(requests, "get", mock_get_request)
    monkeypatch.setattr(semgr8s.k8s_api, "__get_token", kube_token)


class MockResponse:
    content: dict
    headers: dict
    status_code: int = 200

    def __init__(self, content: dict, headers: dict = None, status_code: int = 200):
        self.content = content
        self.headers = headers
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.HTTPError

    def json(self):
        return self.content


def mock_get_request(url, **kwargs):
    kube_regex = [
        (
            r"https:\/\/[^\/]+\/apis?\/(apps\/v1|v1|batch\/v1beta1)"
            r"\/namespaces\/([^\/]+)\/([^\/\?]+)(\/|\?)([^\/]+)"
        ),
        mock_request_kube,
    ]
    kube_namespace_less_regex = [
        (
            r"https:\/\/[^\/]+\/apis?\/(admissionregistration"
            r"\.k8s\.io\/v1beta1)\/[^\/]+\/([^\/]+)"
        ),
        mock_request_kube_namespace_less,
    ]

    for reg in (
        kube_regex,
        kube_namespace_less_regex,
    ):
        match = re.search(reg[0], url)

        if match:
            return reg[1](match, **kwargs)
    return MockResponse({}, status_code=500)


def mock_request_kube(match: re.Match, **kwargs):
    version, namespace, kind, name = (
        match.group(1),
        match.group(2),
        match.group(3),
        match.group(4),
    )

    try:
        return MockResponse(get_k8s_res(kind, namespace))
    except FileNotFoundError as err:
        return MockResponse({}, status_code=500)


def kube_token(path: str):
    return ""


def mock_request_kube_namespace_less(match: re.Match, **kwargs):
    name = match.group(2)
    return MockResponse(get_k8s_res(name))
