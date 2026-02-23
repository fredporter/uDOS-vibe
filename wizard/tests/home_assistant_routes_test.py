"""
Tests for Home Assistant bridge routes.

Coverage:
- GET /api/ha/status — always returns without auth; reflects enabled/disabled state
- GET /api/ha/discover — requires bridge enabled; returns entity list
- POST /api/ha/command — requires bridge enabled; validates allowlist
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes import home_assistant_routes as routes
from wizard.services import home_assistant_service as svc_module


def _app(enabled: bool = True) -> tuple[FastAPI, TestClient]:
    app = FastAPI()
    router = routes.create_ha_routes()
    app.include_router(router)
    return app, TestClient(app)


def _monkeypatch_enabled(monkeypatch, enabled: bool) -> None:
    monkeypatch.setattr(
        svc_module.HomeAssistantService,
        "is_enabled",
        lambda self: enabled,
    )


# ---------------------------------------------------------------------------
# GET /api/ha/status
# ---------------------------------------------------------------------------


def test_status_when_disabled(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    _, client = _app()
    res = client.get("/api/ha/status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "disabled"
    assert body["enabled"] is False
    assert body["bridge"] == "udos-ha"
    assert "version" in body


def test_status_when_enabled(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.get("/api/ha/status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["enabled"] is True


# ---------------------------------------------------------------------------
# GET /api/ha/discover
# ---------------------------------------------------------------------------


def test_discover_when_disabled_returns_503(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    _, client = _app()
    res = client.get("/api/ha/discover")
    assert res.status_code == 503
    assert "disabled" in res.json()["detail"].lower()


def test_discover_when_enabled_returns_entities(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.get("/api/ha/discover")
    assert res.status_code == 200
    body = res.json()
    assert body["bridge"] == "udos-ha"
    assert isinstance(body["entities"], list)
    assert body["entity_count"] == len(body["entities"])
    ids = [e["id"] for e in body["entities"]]
    assert "udos.uhome.tuner" in ids
    assert "udos.uhome.dvr" in ids


# ---------------------------------------------------------------------------
# POST /api/ha/command
# ---------------------------------------------------------------------------


def test_command_when_disabled_returns_503(monkeypatch):
    _monkeypatch_enabled(monkeypatch, False)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.info"})
    assert res.status_code == 503


def test_command_not_in_allowlist_returns_400(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.destroy_everything"})
    assert res.status_code == 400
    assert "allowlist" in res.json()["detail"]


def test_command_system_info(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.info"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["result"]["command"] == "system.info"


def test_command_system_capabilities(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post("/api/ha/command", json={"command": "system.capabilities"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    caps = body["result"]["result"]["allowlist"]
    assert "system.info" in caps
    assert "uhome.tuner.discover" in caps


def test_command_uhome_stub(monkeypatch):
    _monkeypatch_enabled(monkeypatch, True)
    _, client = _app()
    res = client.post(
        "/api/ha/command",
        json={"command": "uhome.tuner.discover", "params": {"timeout": 5}},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    result = body["result"]
    assert result["command"] == "uhome.tuner.discover"
    assert result["status"] == "stub"


def test_command_missing_command_field_returns_422():
    _, client = _app()
    res = client.post("/api/ha/command", json={"params": {}})
    assert res.status_code == 422
