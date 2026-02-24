"""Input Router for Vibe-CLI.

Determines routing destination for user input using deterministic priority:
1. ucode commands (if valid command syntax)
2. Shell commands (if shell enabled and syntax valid)
3. Provider fallback (for natural language)

This enforces command-first execution (not assistant-first).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from core.services.command_dispatch_service import (
    DispatchConfig,
    match_ucode_command,
    validate_shell_command,
)
from core.services.logging_manager import get_logger


class RouteType(Enum):
    """Routing destination types."""

    UCODE_COMMAND = auto()  # Execute as ucode command
    SHELL_COMMAND = auto()  # Execute as shell command
    PROVIDER_FALLBACK = auto()  # Route to OK provider
    SYNTAX_ERROR = auto()  # Invalid input


@dataclass
class RouteDecision:
    """Result of input routing."""

    route_type: RouteType
    command: str | None = None
    confidence: float = 0.0
    error: str | None = None
    metadata: dict | None = None


class InputRouter:
    """Route user input to appropriate execution path.

    Priority order (command-first):
    1. ucode command (if confidence >= threshold)
    2. Shell command (if enabled and valid)
    3. Provider fallback (natural language)
    """

    def __init__(
        self, *, shell_enabled: bool = False, ucode_confidence_threshold: float = 0.80
    ):
        """Initialize input router.

        Args:
            shell_enabled: Whether shell routing is enabled
            ucode_confidence_threshold: Minimum confidence for ucode match
        """
        self.shell_enabled = shell_enabled
        self.ucode_threshold = ucode_confidence_threshold
        self.logger = get_logger("vibe", category="router")

        # Create dispatch config for shell validation
        self.dispatch_config = DispatchConfig(shell_enabled=shell_enabled)

    def route(self, user_input: str) -> RouteDecision:
        """Determine routing destination for user input.

        Args:
            user_input: Raw user input string

        Returns:
            RouteDecision with routing destination and metadata
        """
        if not user_input or not user_input.strip():
            return RouteDecision(route_type=RouteType.SYNTAX_ERROR, error="Empty input")

        user_input = user_input.strip()

        # Stage 1: Try ucode command matching
        ucode_decision = self._try_ucode_match(user_input)
        if ucode_decision.route_type == RouteType.UCODE_COMMAND:
            return ucode_decision

        # Stage 2: Try shell command (if enabled)
        if self.shell_enabled:
            shell_decision = self._try_shell_match(user_input)
            if shell_decision.route_type == RouteType.SHELL_COMMAND:
                return shell_decision

        # Stage 3: Fallback to provider
        return RouteDecision(
            route_type=RouteType.PROVIDER_FALLBACK,
            metadata={"original_input": user_input},
        )

    def _try_ucode_match(self, user_input: str) -> RouteDecision:
        """Try to match input as ucode command.

        Args:
            user_input: User input string

        Returns:
            RouteDecision with ucode match result
        """
        command, confidence = match_ucode_command(user_input)

        if command and confidence >= self.ucode_threshold:
            self.logger.debug(
                f"[Router] ucode match: {command} (confidence: {confidence:.2f})"
            )
            return RouteDecision(
                route_type=RouteType.UCODE_COMMAND,
                command=command,
                confidence=confidence,
                metadata={"original_input": user_input},
            )

        # No match or low confidence
        return RouteDecision(
            route_type=RouteType.PROVIDER_FALLBACK,
            metadata={
                "ucode_attempted": True,
                "ucode_command": command,
                "ucode_confidence": confidence,
            },
        )

    def _try_shell_match(self, user_input: str) -> RouteDecision:
        """Try to match input as shell command.

        Args:
            user_input: User input string

        Returns:
            RouteDecision with shell match result
        """
        is_safe, reason = validate_shell_command(user_input, self.dispatch_config)

        if is_safe:
            self.logger.debug(f"[Router] shell command: {user_input}")
            return RouteDecision(
                route_type=RouteType.SHELL_COMMAND,
                command=user_input,
                metadata={"validation_reason": reason},
            )

        # Not a valid shell command
        self.logger.debug(f"[Router] shell rejected: {reason}")
        return RouteDecision(
            route_type=RouteType.PROVIDER_FALLBACK,
            metadata={"shell_attempted": True, "shell_reason": reason},
        )
