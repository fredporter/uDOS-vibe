"""Adapter protocol for canonical launch orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from wizard.services.launch_orchestrator import LaunchIntent


@dataclass(frozen=True)
class LaunchAdapterExecution:
    final_state: str
    error: str | None = None
    session_updates: dict[str, Any] = field(default_factory=dict)
    state_payload: dict[str, Any] = field(default_factory=dict)


class LaunchAdapter(Protocol):
    def starting_state(self, intent: LaunchIntent) -> str:
        """Return lifecycle state used immediately after planned session creation."""

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        """Run adapter-specific action and return canonical execution details."""
