import io
import threading
import time

import pytest

from core.tui.ucode import IOLifecyclePhase, UCODE


class _TTYBuffer(io.StringIO):
    def isatty(self):
        return True


class _FakeStatusBar:
    def get_status_line(self, user_role="ghost", ghost_mode=False):
        return f"[MODE:{user_role}]"


class _FakeRenderer:
    def __init__(self):
        self.mood = "idle"

    def get_mood(self):
        return self.mood

    def set_mood(self, mood, pace=0.7, blink=True):
        self.mood = mood


def _bare_ucode():
    ucode = UCODE.__new__(UCODE)
    ucode._io_phase = IOLifecyclePhase.BACKGROUND
    ucode._io_phase_lock = threading.RLock()
    ucode.quiet = False
    ucode.status_bar = _FakeStatusBar()
    ucode._theme_text = lambda s: s
    ucode.renderer = _FakeRenderer()
    return ucode


def test_io_phase_scope_restores_previous_phase():
    ucode = _bare_ucode()
    ucode._set_io_phase(IOLifecyclePhase.BACKGROUND)

    with ucode._io_phase_scope(IOLifecyclePhase.INPUT):
        assert ucode._get_io_phase() == IOLifecyclePhase.INPUT

    assert ucode._get_io_phase() == IOLifecyclePhase.BACKGROUND


def test_status_bar_renders_only_in_input_phase(monkeypatch):
    ucode = _bare_ucode()
    buffer = _TTYBuffer()
    monkeypatch.setattr("sys.stdout", buffer)
    monkeypatch.delenv("UDOS_TUI_FORCE_STATUS", raising=False)

    ucode._set_io_phase(IOLifecyclePhase.BACKGROUND)
    ucode._show_status_bar()
    assert buffer.getvalue() == ""

    ucode._set_io_phase(IOLifecyclePhase.INPUT)
    ucode._show_status_bar()
    assert "[MODE:" in buffer.getvalue()


def test_run_with_spinner_executes_work_in_background_phase(monkeypatch):
    ucode = _bare_ucode()
    phase_seen = {"value": None}

    class _FakeSpinner:
        def __init__(self, label, show_elapsed=True):
            self.interval = 0.001

        def start(self):
            return None

        def tick(self):
            return None

        def stop(self, success_text=None):
            return None

    monkeypatch.setattr("core.tui.ui_elements.Spinner", _FakeSpinner)
    ucode._set_io_phase(IOLifecyclePhase.RENDER)

    def _work():
        phase_seen["value"] = ucode._get_io_phase()
        time.sleep(0.01)
        return "ok"

    result = ucode._run_with_spinner("test", _work)
    assert result == "ok"
    assert phase_seen["value"] == IOLifecyclePhase.BACKGROUND
    assert ucode._get_io_phase() == IOLifecyclePhase.RENDER
