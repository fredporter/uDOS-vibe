from __future__ import annotations

from dataclasses import dataclass

from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import LaunchIntent, LaunchOrchestrator


@dataclass(frozen=True)
class _Adapter:
    def starting_state(self, intent: LaunchIntent) -> str:
        return "starting"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        return LaunchAdapterExecution(final_state="ready", state_payload={"ok": True})


def test_launch_orchestrator_includes_thin_gui_contract(tmp_path):
    orchestrator = LaunchOrchestrator(repo_root=tmp_path)
    intent = LaunchIntent(target="media-console", mode="media", launcher="kodi")

    payload = orchestrator.execute(intent, _Adapter())
    state = payload["state"]
    session_id = state["session_id"]

    assert state["state"] == "ready"
    assert state["thin_gui"]["component"] == "extensions/thin-gui"
    assert state["thin_gui"]["contract"] == "launch-intent-v1"
    assert state["thin_gui"]["session"]["id"] == session_id
    assert state["thin_gui"]["session"]["stream"].endswith(f"/launch/sessions/{session_id}/stream")
