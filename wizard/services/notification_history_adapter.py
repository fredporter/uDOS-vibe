"""Synchronous adapter wrapping NotificationHistoryService.

Registered with ``CoreProviderRegistry`` at Wizard startup so Core's
notification helpers write to the SQLite backend instead of JSONL when
the Wizard server is running.

The adapter intentionally avoids ``asyncio`` — all SQLite I/O is
performed synchronously, which is safe because SQLite writes are fast
and Core's callers are synchronous.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from wizard.services.notification_history_service import NotificationHistoryService


class NotificationHistoryAdapter:
    """Sync Protocol implementation backed by NotificationHistoryService."""

    def __init__(self, service: NotificationHistoryService) -> None:
        self._db_path = service.db_path

    def record(self, entry: dict[str, Any]) -> None:
        """Persist *entry* to the SQLite notifications table."""
        notification_id = f"core-{uuid.uuid4().hex[:12]}"
        timestamp = entry.get("timestamp") or datetime.now(timezone.utc).isoformat()
        message = entry.get("message", "Notification triggered")
        # Map core entry fields to DB columns.
        type_ = entry.get("context") or entry.get("source") or "info"
        title: str | None = entry.get("event") or entry.get("context")
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO notifications
                        (id, type, title, message, timestamp, duration_ms, sticky)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                    """,
                    (notification_id, type_, title, message, timestamp),
                )
                conn.commit()
        except Exception:
            pass  # Silently swallow — caller has JSONL fallback

    def get_recent(self, limit: int = 5) -> list[dict[str, Any]]:
        """Return up to *limit* most-recent notifications, newest first."""
        if not self._db_path.exists():
            return []
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM notifications ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        except Exception:
            return []
