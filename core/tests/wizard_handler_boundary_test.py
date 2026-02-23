from __future__ import annotations

from core.commands.wizard_handler import WizardHandler


def test_wizard_connect_host_allows_loopback() -> None:
    handler = WizardHandler()
    assert handler._wizard_connect_host("localhost") == "localhost"
    assert handler._wizard_connect_host("127.0.0.1") == "127.0.0.1"
    assert handler._wizard_connect_host("0.0.0.0") == "127.0.0.1"


def test_wizard_connect_host_blocks_non_loopback() -> None:
    handler = WizardHandler()
    assert handler._wizard_connect_host("wizard.example.com") == "127.0.0.1"


def test_wizard_urls_enforce_loopback_host(monkeypatch) -> None:
    handler = WizardHandler()
    monkeypatch.setattr(handler, "_wizard_host_port", lambda: ("wizard.example.com", 8765))
    base_url, dashboard_url = handler._wizard_urls()
    assert base_url == "http://127.0.0.1:8765"
    assert dashboard_url == "http://127.0.0.1:8765/dashboard"
