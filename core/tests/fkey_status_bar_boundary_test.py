from __future__ import annotations

from core.tui.fkey_handler import FKeyHandler
from core.tui.status_bar import ServerStatus, TUIStatusBar


def test_fkey_wizard_connect_host_blocks_non_loopback() -> None:
    handler = FKeyHandler()
    assert handler._wizard_connect_host("wizard.example.com") == "127.0.0.1"


def test_fkey_wizard_urls_enforce_loopback_host(monkeypatch) -> None:
    handler = FKeyHandler()
    monkeypatch.setattr(handler, "_wizard_host_port", lambda: ("10.1.2.3", 8765))
    base_url, dashboard_url = handler._wizard_urls()
    assert base_url == "http://127.0.0.1:8765"
    assert dashboard_url == "http://127.0.0.1:8765/dashboard"


def test_status_bar_check_server_rejects_non_loopback_host() -> None:
    assert TUIStatusBar._check_server("wizard.example.com", 8765) == ServerStatus.UNKNOWN
