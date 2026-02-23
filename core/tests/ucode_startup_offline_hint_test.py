from __future__ import annotations

from core.tui.ucode import UCODE


def _ucode_stub() -> UCODE:
    ucode = UCODE.__new__(UCODE)
    ucode.quiet = False
    return ucode


def test_show_first_run_offline_hint_includes_minimum_offline_commands(monkeypatch) -> None:
    ucode = _ucode_stub()
    emitted: list[str] = []
    monkeypatch.setattr(ucode, "_network_online", lambda: False)
    monkeypatch.setattr(ucode, "_emit_lines", lambda lines: emitted.extend(lines))

    class _ConfigSyncStub:
        def load_identity_from_env(self) -> dict[str, str]:
            return {}

    monkeypatch.setattr(
        "core.services.config_sync_service.ConfigSyncManager",
        _ConfigSyncStub,
    )

    ucode._show_first_run_offline_hint()

    assert "No network detected. Using offline mode." in emitted
    assert "  UCODE DEMO LIST" in emitted
    assert "  UCODE DOCS --query <text>" in emitted
    assert "  UCODE SYSTEM INFO" in emitted
    assert "  UCODE CAPABILITIES --filter <text>" in emitted


def test_show_first_run_offline_hint_skips_when_online(monkeypatch) -> None:
    ucode = _ucode_stub()
    emitted: list[str] = []
    monkeypatch.setattr(ucode, "_network_online", lambda: True)
    monkeypatch.setattr(ucode, "_emit_lines", lambda lines: emitted.extend(lines))

    ucode._show_first_run_offline_hint()

    assert emitted == []
