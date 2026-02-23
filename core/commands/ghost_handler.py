"""GHOST command handler - inspect Ghost Mode status/policy."""

from __future__ import annotations

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.user_service import is_ghost_mode
from core.tui.output import OutputToolkit


class GhostHandler(BaseCommandHandler):
    """Handler for GHOST command."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        active = is_ghost_mode()
        state = "ACTIVE" if active else "INACTIVE"
        lines = [
            OutputToolkit.banner("GHOST"),
            f"Mode: {state}",
            "",
            "Policy:",
            "- Safe first-run/demo mode with read-only protections.",
            "- Also used as recovery mode after fatal errors or reset flows.",
            "- Write-capable commands are blocked or forced dry-run.",
            "- Use SETUP to exit Ghost Mode and create full user identity.",
        ]
        return {
            "status": "success",
            "message": f"Ghost Mode {state.lower()}",
            "output": "\n".join(lines),
            "ghost_mode": active,
        }
