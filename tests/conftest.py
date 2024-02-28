import json
from contextlib import contextmanager

import pytest

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
            "deployments",
            "deployments_forbiddenlabel",
            "pods",
            "pods_forbiddenlabel",
        )
    ]
