from __future__ import annotations

from core.commands.run_handler import RunHandler
from core.services.mode_policy import RuntimeMode


def test_run_python_requires_dev_mode(monkeypatch):
    handler = RunHandler()
    monkeypatch.setattr("core.commands.run_handler.resolve_runtime_mode", lambda: RuntimeMode.USER)
    monkeypatch.setenv("UDOS_ENFORCE_MODE_BOUNDARIES", "1")
    result = handler.handle("RUN", ["--py", "tools/example.py"])
    assert result["status"] == "warning"
    assert "restricted" in result["message"].lower()
