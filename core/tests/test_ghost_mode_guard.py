import importlib


def _set_ghost_mode(monkeypatch, enabled: bool):
    guard = importlib.import_module("core.commands.ghost_mode_guard")
    monkeypatch.setattr(guard, "is_ghost_mode", lambda: enabled)
    return guard


def test_ghost_mode_guard_allows_when_disabled(monkeypatch):
    guard = _set_ghost_mode(monkeypatch, False)
    assert guard.ghost_mode_block("RUN", ["script.md"]) is None


def test_ghost_mode_guard_allows_read_only_subcommands(monkeypatch):
    guard = _set_ghost_mode(monkeypatch, True)
    assert guard.ghost_mode_block("RUN", ["PARSE", "script.md"]) is None
    assert guard.ghost_mode_block("CONFIG", ["USER_ROLE"]) is None
    assert guard.ghost_mode_block("PROVIDER", ["LIST"]) is None
    assert guard.ghost_mode_block("PROVIDER", ["STATUS", "mistral"]) is None
    assert guard.ghost_mode_block("INTEGRATION", ["STATUS"]) is None
    assert guard.ghost_mode_block("MIGRATE", ["CHECK"]) is None
    assert guard.ghost_mode_block("USER", ["LIST"]) is None
    assert guard.ghost_mode_block("UID", []) is None
    assert guard.ghost_mode_block("DATASET", ["LIST"]) is None
    assert guard.ghost_mode_block("SONIC", ["STATUS"]) is None
    assert guard.ghost_mode_block("HOTKEYS", []) is None
    assert guard.ghost_mode_block("PATTERN", ["LIST"]) is None
    assert guard.ghost_mode_block("SEED", ["STATUS"]) is None
    assert guard.ghost_mode_block("PLUGIN", ["LIST"]) is None
    assert guard.ghost_mode_block("WIZARD", ["STATUS"]) is None
    assert guard.ghost_mode_block("BINDER", ["PICK"]) is None


def test_ghost_mode_guard_blocks_or_dry_runs(monkeypatch):
    guard = _set_ghost_mode(monkeypatch, True)

    blocked = guard.ghost_mode_block("RUN", ["script.md"])
    assert blocked and blocked.get("status") == "warning"

    dry_run = guard.ghost_mode_block("CONFIG", ["USER_ROLE", "admin"])
    assert dry_run and dry_run.get("dry_run") is True

    blocked = guard.ghost_mode_block("PLUGIN", ["INSTALL", "foo"])
    assert blocked and blocked.get("status") == "warning"

    blocked = guard.ghost_mode_block("BINDER", ["COMPILE", "demo"])
    assert blocked and blocked.get("status") == "warning"

    blocked = guard.ghost_mode_block("SEED", ["INSTALL"])
    assert blocked and blocked.get("status") == "warning"

    blocked = guard.ghost_mode_block("WIZARD", ["START"])
    assert blocked and blocked.get("status") == "warning"
