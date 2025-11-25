import importlib.util
from pathlib import Path
from types import SimpleNamespace

import requests


def _load_aider_client_module():
    # test file is at .../ai-school/tests/, clients are under .../ai-school/clients/
    root = Path(__file__).parents[1]
    mod_path = root / "clients" / "aider_client.py"
    spec = importlib.util.spec_from_file_location("aider_client_mod", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_resp(status=200, headers=None, text="", json_obj=None):
    m = SimpleNamespace()
    m.status_code = status
    m.headers = headers or {}
    m.text = text

    def _json():
        if json_obj is None:
            raise ValueError("no json")
        return json_obj

    m.json = _json
    return m


def test_ask_success_text(monkeypatch):
    mod = _load_aider_client_module()
    AiderClient = mod.AiderClient

    resp = make_resp(status=200, headers={"Content-Type": "text/plain"}, text="OK")

    monkeypatch.setattr(requests, "post", lambda *a, **k: resp)

    client = AiderClient(endpoint="http://example")
    ok, msg = client.ask("ping")
    assert ok is True
    assert msg == "OK"


def test_ask_success_json(monkeypatch):
    mod = _load_aider_client_module()
    AiderClient = mod.AiderClient

    resp = make_resp(
        status=200,
        headers={"Content-Type": "application/json"},
        json_obj={"text": "hello"},
    )

    monkeypatch.setattr(requests, "post", lambda *a, **k: resp)

    client = AiderClient(endpoint="http://example")
    ok, msg = client.ask("ping")
    assert ok is True
    assert msg == "hello"


def test_ask_http_error_all_paths(monkeypatch):
    mod = _load_aider_client_module()
    AiderClient = mod.AiderClient

    resp = make_resp(
        status=404, headers={"Content-Type": "text/plain"}, text="Not Found"
    )
    monkeypatch.setattr(requests, "post", lambda *a, **k: resp)

    client = AiderClient(endpoint="http://example")
    ok, msg = client.ask("ping")
    assert ok is False
    assert msg.startswith("[error]")
    assert "HTTP 404" in msg


def test_ask_connection_error(monkeypatch):
    mod = _load_aider_client_module()
    AiderClient = mod.AiderClient

    def _raise(*a, **k):
        raise requests.exceptions.ConnectionError("conn fail")

    monkeypatch.setattr(requests, "post", _raise)

    client = AiderClient(endpoint="http://example")
    ok, msg = client.ask("ping")
    assert ok is False
    assert msg.startswith("[error]")
    assert "conn fail" in msg or "ConnectionError" in msg
