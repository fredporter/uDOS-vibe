"""Thin GUI contract payloads for launch/session consumers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wizard.services.launch_orchestrator import LaunchIntent

THIN_GUI_COMPONENT = "extensions/thin-gui"
THIN_GUI_CONTRACT_VERSION = "launch-intent-v1"


def build_thin_gui_contract(intent: LaunchIntent, session_id: str) -> dict[str, Any]:
    """Return a UI-facing contract for launch intent + session stream handling."""
    return {
        "component": THIN_GUI_COMPONENT,
        "contract": THIN_GUI_CONTRACT_VERSION,
        "intent": {
            "target": intent.target,
            "mode": intent.mode,
            "launcher": intent.launcher,
            "workspace": intent.workspace,
            "profile_id": intent.profile_id,
        },
        "session": {
            "id": session_id,
            "get": f"/api/platform/launch/sessions/{session_id}",
            "stream": f"/api/platform/launch/sessions/{session_id}/stream",
        },
    }
