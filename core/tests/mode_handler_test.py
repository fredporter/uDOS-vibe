from __future__ import annotations

from core.commands.mode_handler import ModeHandler
from core.tui.dispatcher import CommandDispatcher


def test_mode_status_includes_theme(monkeypatch):
    monkeypatch.setenv("UDOS_DEFAULT_USER", "admin")
    handler = ModeHandler()
    result = handler.handle("MODE", ["STATUS"])
    assert result["status"] == "success"
    assert "Theme:" in result["output"]


def test_mode_theme_bridge_tags_output(monkeypatch):
    monkeypatch.setenv("UDOS_DEFAULT_USER", "admin")
    handler = ModeHandler()
    result = handler.handle("MODE", ["THEME", "LIST"])
    assert result["status"] in {"success", "warning"}
    assert "[RETHEME-CANDIDATE:theme-lingo]" in result["output"]


def test_mode_registered_in_dispatcher(monkeypatch):
    monkeypatch.setenv("UDOS_DEFAULT_USER", "admin")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("MODE STATUS")
    assert result["status"] == "success"
    assert "MODE STATUS" in result["output"]


def test_status_alias_routes_to_mode_status(monkeypatch):
    monkeypatch.setenv("UDOS_DEFAULT_USER", "admin")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("STATUS --compact")
    assert result["status"] == "success"
    assert result["output"].startswith("MODE:")


def test_mode_status_compact_includes_skin_lens_progression(monkeypatch):
    monkeypatch.setenv("UDOS_DEFAULT_USER", "admin")
    handler = ModeHandler()
    result = handler.handle("MODE", ["STATUS", "--compact"])
    assert result["status"] == "success"
    output = result["output"]
    assert output.startswith("MODE:")
    assert "theme=" in output
    assert "lens=" in output
    assert "skin=" in output
    assert "fit=" in output
    assert "xp=" in output
    assert "gold=" in output
    assert "ach=" in output
