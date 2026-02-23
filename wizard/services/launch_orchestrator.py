"""Shared launch orchestration for Wizard platform adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from wizard.services.launch_adapters import LaunchAdapter
from wizard.services.launch_session_service import (
    LaunchSessionService,
    get_launch_session_service,
)
from wizard.services.thin_gui_contract import build_thin_gui_contract


@dataclass(frozen=True)
class LaunchIntent:
    target: str
    mode: str
    launcher: str | None = None
    workspace: str | None = None
    profile_id: str | None = None
    auth: dict[str, Any] = field(default_factory=dict)


class LaunchOrchestrator:
    """Create and transition launch sessions with a canonical flow."""

    def __init__(self, repo_root: Path | None = None):
        self.sessions: LaunchSessionService = get_launch_session_service(repo_root=repo_root)

    def execute(self, intent: LaunchIntent, adapter: LaunchAdapter) -> dict[str, Any]:
        """Execute a launch intent via an adapter and return canonical session/state."""
        session = self.sessions.create_session(
            target=intent.target,
            mode=intent.mode,
            launcher=intent.launcher,
            workspace=intent.workspace,
            profile_id=intent.profile_id,
            auth=dict(intent.auth),
            state="planned",
        )
        started = self.sessions.transition(
            session["session_id"],
            adapter.starting_state(intent),
        )
        execution = adapter.execute(intent)
        final_session = self.sessions.transition(
            started["session_id"],
            execution.final_state,
            error=execution.error,
            updates=execution.session_updates,
        )
        state_payload = dict(execution.state_payload)
        state_payload["session_id"] = final_session["session_id"]
        state_payload["state"] = final_session["state"]
        state_payload["thin_gui"] = build_thin_gui_contract(intent, final_session["session_id"])
        return {"session": final_session, "state": state_payload}


def get_launch_orchestrator(repo_root: Path | None = None) -> LaunchOrchestrator:
    return LaunchOrchestrator(repo_root=repo_root)
