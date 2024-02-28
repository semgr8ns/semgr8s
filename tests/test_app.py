import pytest

from . import conftest as fix


@pytest.fixture(autouse=True)
def set_envs(monkeypatch):
    monkeypatch.setenv("SEMGREP_RULES", "")


@pytest.fixture(autouse=True)
def set_flask_app(monkeypatch):
    import semgr8s.app as sapp

    pytest.sapp = sapp


@pytest.mark.parametrize(
    "index, allowed, msg",
    [(2, True, "Compliant resource admitted"), (3, False, "forbidden-label")],
)
def test_validate(monkeypatch, adm_req_samples, index, allowed, msg):
    client = pytest.sapp.APP.test_client()
    response = client.post("/validate", json=adm_req_samples[index])
    assert response.is_json
    assert response.status_code == 200
    admission_response = response.get_json()["response"]
    assert admission_response["allowed"] == allowed
    assert msg in admission_response["status"]["message"]
