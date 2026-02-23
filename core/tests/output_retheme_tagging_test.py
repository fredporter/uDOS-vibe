from __future__ import annotations

from core.tui.output import OutputToolkit


def test_retheme_tagging_does_not_mark_tip_health_info_by_default(monkeypatch) -> None:
    monkeypatch.setenv(OutputToolkit.RETHEME_TAG_ENV, "1")
    monkeypatch.delenv(OutputToolkit.RETHEME_INFO_PREFIX_ENV, raising=False)
    line = OutputToolkit.line("Tip: use PLAY OPTIONS", level="info")
    assert OutputToolkit.RETHEME_MARKER not in line
    line = OutputToolkit.line("Health: nominal", level="info")
    assert OutputToolkit.RETHEME_MARKER not in line


def test_retheme_tagging_marks_warn_error(monkeypatch) -> None:
    monkeypatch.setenv(OutputToolkit.RETHEME_TAG_ENV, "1")
    warn_line = OutputToolkit.line("Something might drift", level="warn")
    assert OutputToolkit.RETHEME_MARKER in warn_line
    err_line = OutputToolkit.alert("Failure path", level="error")
    assert OutputToolkit.RETHEME_MARKER in err_line

