import base64
import json
import pytest

from . import conftest as fix


@pytest.fixture(autouse=True)
def set_envs(monkeypatch):
    monkeypatch.setenv("SEMGREP_RULES", "")


@pytest.fixture(autouse=True)
def set_flask_app(monkeypatch):
    import semgr8s.app as sapp

    pytest.sapp = sapp


def test_healthz():
    client = pytest.sapp.APP.test_client()
    get_response = client.get("/health")
    post_response = client.post("/health")
    assert get_response.status_code == 200
    assert post_response.status_code == 200


def test_readyz():
    client = pytest.sapp.APP.test_client()
    get_response = client.get("/ready")
    post_response = client.post("/ready")
    assert get_response.status_code == 200
    assert post_response.status_code == 200


@pytest.mark.parametrize(
    "index, remote_rules, allowed, code, msg",
    [
        (5, "", True, 201, "Compliant resource admitted"),
        (0, "", False, 400, "no payload.request found"),
        (1, "", False, 400, "no payload.request found"),
        (6, "", False, 403, "forbidden-label"),
        (None, "", False, 415, "Unsupported Media Type"),
        (5, "foobar/random-e3b0c4", False, 418, "error during semgrep scan"),
        (2, "", False, 422, "no payload.request.uid found"),
    ],
)
def test_validate(
    monkeypatch, adm_req_samples, index, remote_rules, allowed, code, msg
):
    monkeypatch.setenv("SEMGREP_RULES", remote_rules)
    client = pytest.sapp.APP.test_client()
    if index is not None:
        payload = adm_req_samples[index]
    else:
        payload = ""
    response = client.post("/validate", json=payload)
    assert response.is_json
    assert response.status_code == 200
    admission_response = response.get_json()["response"]
    assert admission_response["allowed"] == allowed
    assert admission_response["status"]["code"] == code
    assert msg in admission_response["status"]["message"]


@pytest.mark.parametrize(
    "index, remote_rules, allowed, code, msg, patch",
    [
        (5, "", True, 201, "Compliant resource admitted", None),
        (
            6,
            "",
            True,
            202,
            "forbidden-label",
            '[{"op": "remove", "path": "/metadata/labels/semgr8s-test"}]',
        ),
    ],
)
def test_mutate(
    monkeypatch, adm_req_samples, index, remote_rules, allowed, code, msg, patch
):
    monkeypatch.setenv("SEMGREP_RULES", remote_rules)
    client = pytest.sapp.APP.test_client()
    if index is not None:
        payload = adm_req_samples[index]
    else:
        payload = ""
    response = client.post("/mutate", json=payload)
    assert response.is_json
    assert response.status_code == 200
    admission_response = response.get_json()["response"]
    assert admission_response["allowed"] == allowed
    assert admission_response["status"]["code"] == code
    assert msg in admission_response["status"]["message"]
    if patch:
        assert admission_response["patchType"] == "JSONPatch"
        assert admission_response["patch"] == base64.b64encode(
            bytearray(json.dumps(json.loads(patch)), "utf-8")
        ).decode("utf-8")
