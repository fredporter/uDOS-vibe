"""Command Engine for Vibe-CLI.

Executes ucode commands with deterministic short-circuit behavior.
NO provider interaction. NO double execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.services.logging_manager import get_logger


@dataclass
class ExecutionResult:
    """Result of command execution."""

    status: str  # "success" | "error"
    output: str | None = None
    message: str | None = None
    command: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class CommandEngine:
    """Execute ucode commands with short-circuit logic.

    This engine ensures:
    - Deterministic execution
    - No provider calls during command execution
    - Hard stop after execution (no fallback)
    - Clean error handling
    """

    def __init__(self):
        """Initialize command engine."""
        self.logger = get_logger("vibe", category="command-engine")

    def execute_ucode(self, command: str, dispatcher: Any = None) -> ExecutionResult:
        """Execute ucode command with short-circuit.

        Args:
            command: ucode command string (e.g., "HELP" or "STATUS")
            dispatcher: Optional CommandDispatcher instance

        Returns:
            ExecutionResult with output and status

        Note:
            This executes and returns immediately.
            NO provider interaction. NO fallback.
        """
        if not command or not command.strip():
            return ExecutionResult(
                status="error", error="Empty command", message="Command cannot be empty"
            )

        command = command.strip()

        self.logger.debug(f"[CommandEngine] Executing: {command}")

        try:
            # Get dispatcher
            if dispatcher is None:
                from core.tui.dispatcher import CommandDispatcher

                dispatcher = CommandDispatcher()

            # Execute command
            result = dispatcher.dispatch(command)

            # Extract output
            output = (
                result.get("output")
                or result.get("rendered")
                or result.get("message")
                or ""
            )

            status = result.get("status", "success")

            self.logger.debug(f"[CommandEngine] Executed {command} → {status}")

            return ExecutionResult(
                status=status,
                output=output,
                command=command,
                message=result.get("message"),
                metadata={"dispatch_result": result},
            )

        except Exception as exc:
            self.logger.error(
                f"[CommandEngine] Execution failed: {exc}", extra={"command": command}
            )

            return ExecutionResult(
                status="error",
                error=str(exc),
                command=command,
                message=f"Command execution failed: {exc}",
            )
