"""Notification history provider protocol.

Defines the minimal synchronous interface Core requires from whatever
backend is storing notifications.  Wizard registers a concrete
implementation (SQLite) at startup via CoreProviderRegistry; the JSONL
fallback in ``notification_history_service.py`` is used when Wizard is
absent.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class NotificationHistoryProtocol(Protocol):
    """Synchronous notification history operations used by Core."""

    def record(self, entry: dict) -> None:
        """Persist a notification entry dict (requires at least 'message' key)."""
        ...

    def get_recent(self, limit: int = 5) -> list[dict]:
        """Return up to *limit* most-recent notification entries, newest first."""
        ...
