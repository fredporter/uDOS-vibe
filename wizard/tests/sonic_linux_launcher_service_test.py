from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from wizard.services.sonic_linux_launcher_service import SonicLinuxLauncherService


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_script(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    path.chmod(0o755)


def test_linux_launcher_service_writes_canonical_launch_session(tmp_path: Path):
    script_path = tmp_path / "distribution" / "udos" / "bin" / "udos-gui"
    _write_script(script_path)

    def _runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="ok", stderr="")

    service = SonicLinuxLauncherService(repo_root=tmp_path, runner=_runner)
    state = service.apply_action(
        "start",
        workspace="/tmp/workspace",
        protocol="openrc",
        execute=True,
    )

    assert state["state"] == "ready"
    assert state["executed"] is True
    assert state["session_id"]
    assert state["command"] == [str(script_path), "start"]

    session = _read_json(tmp_path / "memory" / "wizard" / "launch" / f"{state['session_id']}.json")
    assert session["target"] == "alpine-core-linux-gui"
    assert session["mode"] == "gui"
    assert session["launcher"] == "udos-gui"
    assert session["workspace"] == "/tmp/workspace"
    assert session["protocol"] == "openrc"
    assert session["state"] == "ready"


def test_linux_launcher_service_stop_action_uses_stopped_lifecycle(tmp_path: Path):
    script_path = tmp_path / "distribution" / "udos" / "bin" / "udos-gui"
    _write_script(script_path)

    service = SonicLinuxLauncherService(repo_root=tmp_path)
    state = service.apply_action("stop", protocol="direct", execute=False)

    assert state["state"] == "stopped"
    session = _read_json(tmp_path / "memory" / "wizard" / "launch" / f"{state['session_id']}.json")
    assert session["state"] == "stopped"
    assert session["action"] == "stop"
    assert session["protocol"] == "direct"
    assert session["executed"] is False


def test_linux_launcher_service_rejects_missing_script(tmp_path: Path):
    service = SonicLinuxLauncherService(repo_root=tmp_path)
    with pytest.raises(FileNotFoundError):
        service.apply_action("start")
