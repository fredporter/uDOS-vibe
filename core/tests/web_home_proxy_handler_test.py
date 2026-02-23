from __future__ import annotations

import pytest

from core.commands.home_handler import HomeHandler
from core.commands.web_handler import WebHandler
from core.services.error_contract import CommandError
from core.services.stdlib_http import HTTPError
from core.services.wizard_proxy_service import dispatch_via_wizard


class _WizardManagerStub:
    def __init__(self, *, connected: bool = True) -> None:
        self.connected = connected
        self.called = False

    def ensure_running(self, **_kwargs):
        self.called = True
        return type(
            "WizardStatus",
            (),
            {"connected": self.connected, "message": "ok", "running": self.connected, "pid": 1},
        )()

    def status(self, **_kwargs):
        return type(
            "WizardStatus",
            (),
            {"connected": self.connected, "message": "ok", "running": self.connected, "pid": 1},
        )()


def test_web_status_reports_proxy(monkeypatch):
    handler = WebHandler()

    monkeypatch.setattr(
        "core.commands.web_handler.wizard_proxy_status",
        lambda: {"status": "success", "connected": True},
    )

    result = handler.handle("WEB", ["STATUS"])
    assert result["status"] == "success"
    assert "proxied through local Wizard" in str(result.get("message", ""))


def test_web_fetch_proxies_to_wizard(monkeypatch):
    handler = WebHandler()

    monkeypatch.setattr(
        "core.commands.web_handler.dispatch_via_wizard",
        lambda command: {"status": "success", "command": command},
    )

    result = handler.handle("WEB", ["FETCH", "https://example.com"])
    assert result["status"] == "success"
    assert result["command"] == "WEB FETCH https://example.com"


def test_home_lights_proxies_to_wizard(monkeypatch):
    handler = HomeHandler()

    monkeypatch.setattr(
        "core.commands.home_handler.dispatch_via_wizard",
        lambda command: {"status": "success", "command": command},
    )

    result = handler.handle("HOME", ["LIGHTS"])
    assert result["status"] == "success"
    assert result["command"] == "HOME LIGHTS"


def test_home_unknown_action_raises():
    handler = HomeHandler()
    with pytest.raises(CommandError) as exc:
        handler.handle("HOME", ["WAT"])
    assert exc.value.code == "ERR_COMMAND_NOT_FOUND"


def test_wizard_proxy_rejects_non_loopback(monkeypatch):
    monkeypatch.setenv("WIZARD_BASE_URL", "https://wizard.example.com")
    with pytest.raises(CommandError) as exc:
        dispatch_via_wizard("WEB STATUS")
    assert exc.value.code == "ERR_BOUNDARY_POLICY"


def test_wizard_proxy_maps_auth_error(monkeypatch):
    monkeypatch.setenv("WIZARD_BASE_URL", "http://localhost:8765")
    manager = _WizardManagerStub(connected=True)
    monkeypatch.setattr("core.services.wizard_proxy_service.get_wizard_process_manager", lambda: manager)

    def _raise_auth(*args, **kwargs):
        raise HTTPError(403, "forbidden", '{"detail":"forbidden"}')

    monkeypatch.setattr("core.services.wizard_proxy_service.http_post", _raise_auth)

    with pytest.raises(CommandError) as exc:
        dispatch_via_wizard("WEB STATUS")
    assert exc.value.code == "ERR_AUTH_REQUIRED"


def test_wizard_proxy_dispatch_ensures_wizard_running(monkeypatch):
    monkeypatch.setenv("WIZARD_BASE_URL", "http://localhost:8765")
    manager = _WizardManagerStub(connected=True)
    monkeypatch.setattr("core.services.wizard_proxy_service.get_wizard_process_manager", lambda: manager)
    monkeypatch.setattr(
        "core.services.wizard_proxy_service.http_post",
        lambda *_args, **_kwargs: {"status_code": 200, "json": {"result": {"status": "success"}}},
    )

    result = dispatch_via_wizard("WEB STATUS")

    assert result["status"] == "success"
    assert manager.called
