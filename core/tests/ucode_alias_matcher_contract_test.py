"""Contract checks for uCODE matcher delegation."""

from __future__ import annotations

from core.tui.ucode import UCODE


def _ucode_stub() -> UCODE:
    return UCODE.__new__(UCODE)


def test_ucode_matcher_keeps_local_short_aliases() -> None:
    ucode = _ucode_stub()
    assert ucode._match_ucode_command("? help") == ("HELP", 1.0)
    assert ucode._match_ucode_command("h") == ("HELP", 1.0)
    assert ucode._match_ucode_command("ls") == ("BINDER", 1.0)


def test_ucode_matcher_delegates_to_shared_stage1(monkeypatch) -> None:
    ucode = _ucode_stub()

    def _fake_match(user_input: str) -> tuple[str | None, float]:
        assert user_input == "statu"
        return "STATUS", 0.8

    monkeypatch.setattr("core.tui.ucode.match_ucode_command", _fake_match)
    assert ucode._match_ucode_command("statu") == ("STATUS", 0.8)


def test_question_mode_uses_canonical_dispatch_pipeline(monkeypatch) -> None:
    ucode = _ucode_stub()

    def _fake_dispatch(user_input: str) -> dict[str, str]:
        assert user_input == "help status"
        return {"status": "success", "command": "HELP"}

    monkeypatch.setattr(ucode, "_dispatch_with_vibe", _fake_dispatch)
    assert ucode._handle_question_mode("help status") == {
        "status": "success",
        "command": "HELP",
    }
