"""
Tests for dashboard summary / health aggregation routes.
"""
from __future__ import annotations

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.dashboard_summary_routes import create_dashboard_summary_routes


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(create_dashboard_summary_routes())
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/dashboard/health
# ---------------------------------------------------------------------------


def test_health_returns_200():
    client = _client()
    res = client.get("/api/dashboard/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["bridge"] == "udos-wizard"
    assert "version" in body
    assert "timestamp" in body
    assert "ollama_running" in body


def test_health_ollama_running_true(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(
        mod, "_ollama_status",
        lambda: {"running": True, "version": "0.3.0"},
    )
    body = _client().get("/api/dashboard/health").json()
    assert body["ollama_running"] is True


def test_health_ollama_running_false(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": False})
    body = _client().get("/api/dashboard/health").json()
    assert body["ollama_running"] is False


# ---------------------------------------------------------------------------
# GET /api/dashboard/summary
# ---------------------------------------------------------------------------


def _patch_all_healthy(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": True, "version": "0.3.0"})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": ["mistral"], "primary": "mistral"})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})


def test_summary_returns_200(monkeypatch):
    _patch_all_healthy(monkeypatch)
    res = _client().get("/api/dashboard/summary")
    assert res.status_code == 200


def test_summary_shape(monkeypatch):
    _patch_all_healthy(monkeypatch)
    body = _client().get("/api/dashboard/summary").json()
    assert body["ok"] is True
    assert "subsystems" in body
    assert "summary" in body
    assert set(body["subsystems"].keys()) == {"ollama", "cloud", "ha_bridge", "secret_sync"}


def test_summary_all_healthy(monkeypatch):
    _patch_all_healthy(monkeypatch)
    body = _client().get("/api/dashboard/summary").json()
    assert body["summary"]["healthy"] == 4
    assert body["summary"]["degraded"] == 0


def test_summary_overall_ok_false_when_ollama_down(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    # _ollama_status raises when Ollama is unreachable; _probe catches → ok=False
    monkeypatch.setattr(mod, "_ollama_status", lambda: (_ for _ in ()).throw(RuntimeError("connection refused")))
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": False, "status": "disabled"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    # ollama is a critical subsystem — overall ok should be False
    assert body["ok"] is False
    assert body["subsystems"]["ollama"]["ok"] is False


def test_summary_non_critical_failure_does_not_degrade_ok(monkeypatch):
    """HA bridge down or secret sync failing doesn't mark overall ok=False."""
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": True, "version": "0.3.0"})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": ["mistral"], "primary": "mistral"})
    # Non-critical subsystems raise
    monkeypatch.setattr(mod, "_ha_status", lambda: (_ for _ in ()).throw(RuntimeError("bridge offline")))
    monkeypatch.setattr(mod, "_sync_status", lambda: (_ for _ in ()).throw(RuntimeError("vault locked")))
    body = _client().get("/api/dashboard/summary").json()
    assert body["ok"] is True  # critical subsystems are fine
    assert body["subsystems"]["ha_bridge"]["ok"] is False
    assert body["subsystems"]["secret_sync"]["ok"] is False
    assert body["summary"]["degraded"] == 2


def test_summary_subsystem_error_propagates_message(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": False, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: (_ for _ in ()).throw(ConnectionError("ha unreachable")))
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    ha = body["subsystems"]["ha_bridge"]
    assert ha["ok"] is False
    assert "ha unreachable" in ha["error"]


def test_summary_cloud_details_exposed(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {
        "ready": True, "available_providers": ["mistral", "openai"], "primary": "mistral"
    })
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    cloud = body["subsystems"]["cloud"]
    assert cloud["primary"] == "mistral"
    assert "openai" in cloud["available_providers"]


def test_summary_sync_drift_reported(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_ollama_status", lambda: {"running": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": False, "status": "disabled"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {
        "drift_issues": 2,
        "issues": ["missing_wizard_key", "missing_admin_token"],
        "synced": False,
    })
    body = _client().get("/api/dashboard/summary").json()
    sync = body["subsystems"]["secret_sync"]
    assert sync["drift_issues"] == 2
    assert "missing_wizard_key" in sync["issues"]
