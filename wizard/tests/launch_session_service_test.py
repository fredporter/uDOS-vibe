from __future__ import annotations

import json
from pathlib import Path

from wizard.services.launch_session_service import LaunchSessionService
from wizard.services.sonic_media_console_service import SonicMediaConsoleService
from wizard.services.sonic_windows_launcher_service import SonicWindowsLauncherService


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_launch_session_service_lifecycle_writes_canonical_state(tmp_path):
    service = LaunchSessionService(repo_root=tmp_path)
    created = service.create_session(
        target="windows10-entertainment",
        mode="gaming",
        launcher="playnite",
        workspace=None,
        profile_id="gaming",
        auth={"token": "x"},
        state="planned",
    )
    assert created["state"] == "planned"
    assert created["session_id"].startswith("windows10-entertainment-")

    started = service.transition(created["session_id"], "starting")
    assert started["state"] == "starting"
    ready = service.transition(created["session_id"], "ready")
    assert ready["state"] == "ready"

    state_path = tmp_path / "memory" / "wizard" / "launch" / f"{created['session_id']}.json"
    assert state_path.exists()
    saved = _read_json(state_path)
    assert saved["state"] == "ready"
    assert saved["target"] == "windows10-entertainment"


def test_windows_launcher_service_persists_launch_session(tmp_path):
    service = SonicWindowsLauncherService(repo_root=tmp_path)
    state = service.set_mode("gaming", launcher="playnite")
    assert state["state"] == "ready"
    assert state["session_id"]

    launch_state = _read_json(tmp_path / "memory" / "wizard" / "launch" / f"{state['session_id']}.json")
    assert launch_state["target"] == "windows10-entertainment"
    assert launch_state["mode"] == "gaming"
    assert launch_state["launcher"] == "playnite"
    assert launch_state["state"] == "ready"


def test_media_console_service_persists_start_and_stop_sessions(tmp_path):
    service = SonicMediaConsoleService(repo_root=tmp_path)

    started = service.start("kodi")
    assert started["state"] == "ready"
    start_session = _read_json(tmp_path / "memory" / "wizard" / "launch" / f"{started['session_id']}.json")
    assert start_session["target"] == "media-console"
    assert start_session["state"] == "ready"

    stopped = service.stop()
    assert stopped["state"] == "stopped"
    stop_session = _read_json(tmp_path / "memory" / "wizard" / "launch" / f"{stopped['session_id']}.json")
    assert stop_session["target"] == "media-console"
    assert stop_session["state"] == "stopped"
