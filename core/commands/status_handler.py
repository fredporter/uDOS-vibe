"""STATUS command handler."""

from __future__ import annotations

from typing import Any

from core.commands.base import BaseCommandHandler
from core.commands.mode_handler import ModeHandler


class StatusHandler(BaseCommandHandler):
    """Handler for STATUS command.

    STATUS is a first-class command that delegates to MODE STATUS so all
    dispatch surfaces share one canonical implementation.
    """

    def __init__(self) -> None:
        super().__init__()
        self._mode_handler = ModeHandler()

    def handle(
        self,
        command: str,
        params: list[str],
        grid: Any = None,
        parser: Any = None,
    ) -> dict[str, Any]:
        return self._mode_handler.handle("MODE", ["STATUS", *params], grid=grid, parser=parser)
