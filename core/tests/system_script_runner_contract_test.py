from __future__ import annotations

from pathlib import Path

import core.services.system_script_runner as runner_mod


class _TodoReminderStub:
    def log_reminder(self):
        return {}


class _AutomationMonitorStub:
    def __init__(self, *_args, **_kwargs):
        return

    def summary(self):
        return {"should_gate": False}


def _prepare_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "core" / "framework" / "seed" / "bank" / "system"
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "startup-script.md").write_text("template startup", encoding="utf-8")
    (template_dir / "reboot-script.md").write_text("template reboot", encoding="utf-8")
    return repo_root


def _patch_runtime_dependencies(monkeypatch, repo_root: Path) -> None:
    monkeypatch.setattr(runner_mod, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(runner_mod, "AutomationMonitor", _AutomationMonitorStub)
    monkeypatch.setattr(
        runner_mod,
        "write_hotkey_payload",
        lambda *_args, **_kwargs: {"snapshot": None, "last_updated": None},
    )
    monkeypatch.setattr(runner_mod, "read_hotkey_payload", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(runner_mod, "remind_if_pending", lambda: {})
    monkeypatch.setattr(runner_mod, "get_reminder_service", lambda: _TodoReminderStub())


def test_startup_script_prefers_user_override(monkeypatch, tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    memory_root = tmp_path / "memory"
    user_script = memory_root / "user" / "system" / "startup-script.md"
    user_script.parent.mkdir(parents=True, exist_ok=True)
    user_script.write_text("user override startup", encoding="utf-8")

    monkeypatch.setenv("UDOS_MEMORY_ROOT", str(memory_root))
    _patch_runtime_dependencies(monkeypatch, repo_root)

    selected: dict[str, Path] = {}

    class _TSRuntimeServiceStub:
        def execute(self, script_path: Path):
            selected["script_path"] = script_path
            return {"status": "success", "payload": {"result": {"output": "ok"}}}

    monkeypatch.setattr(runner_mod, "TSRuntimeService", _TSRuntimeServiceStub)

    result = runner_mod.SystemScriptRunner().run_startup_script()

    assert result["status"] == "success"
    assert result["script_path"] == str(user_script)
    assert selected["script_path"] == user_script


def test_startup_script_env_override_wins(monkeypatch, tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    memory_root = tmp_path / "memory"
    env_script = memory_root / "custom" / "startup-from-env.md"
    env_script.parent.mkdir(parents=True, exist_ok=True)
    env_script.write_text("env override startup", encoding="utf-8")
    (memory_root / "user" / "system").mkdir(parents=True, exist_ok=True)
    (memory_root / "user" / "system" / "startup-script.md").write_text(
        "user override startup",
        encoding="utf-8",
    )

    monkeypatch.setenv("UDOS_MEMORY_ROOT", str(memory_root))
    monkeypatch.setenv("UDOS_STARTUP_SCRIPT_PATH", str(env_script))
    _patch_runtime_dependencies(monkeypatch, repo_root)

    selected: dict[str, Path] = {}

    class _TSRuntimeServiceStub:
        def execute(self, script_path: Path):
            selected["script_path"] = script_path
            return {"status": "success", "payload": {"result": {"output": "ok"}}}

    monkeypatch.setattr(runner_mod, "TSRuntimeService", _TSRuntimeServiceStub)

    result = runner_mod.SystemScriptRunner().run_startup_script()

    assert result["status"] == "success"
    assert result["script_path"] == str(env_script)
    assert selected["script_path"] == env_script
