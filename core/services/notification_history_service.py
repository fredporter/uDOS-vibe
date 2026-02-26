"""Notification history recorder for health / automation reminders."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from core.services.health_training import read_last_summary
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("notification-history")


def _ensure_log_path() -> Path:
    root = get_repo_root()
    log_dir = root / "memory" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "notification-history.log"


def _append_entry(entry: Dict) -> None:
    # Prefer wizard SQLite backend when registered.
    try:
        from core.services.provider_registry import ProviderType, is_provider_available, get_provider
        if is_provider_available(ProviderType.NOTIFICATION_HISTORY):
            get_provider(ProviderType.NOTIFICATION_HISTORY).record(entry)
            return
    except Exception as exc:
        logger.warning("[NotificationHistory] Protocol call failed, falling back to JSONL: %s", exc)
    # Fallback: append to local JSONL log.
    try:
        with open(_ensure_log_path(), "a") as handle:
            handle.write(json.dumps(entry) + "\n")
    except Exception as exc:
        logger.warning("[NotificationHistory] Failed to persist entry: %s", exc)


def remind_if_pending() -> Optional[Dict]:
    """Emit a reminder if the latest health log reports remaining self-heal issues."""
    summary = read_last_summary()
    if not summary:
        return None
    remaining = summary.get("self_heal", {}).get("remaining", 0)
    if not remaining:
        return None
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": "self-heal",
        "remaining": remaining,
        "message": f"Self-Heal issues remain: {remaining} unresolved",
        "health_log": summary,
    }
    logger.warning("[Notification] %s", entry["message"])
    _append_entry(entry)
    return entry


def record_notification(entry: Dict) -> None:
    """Store arbitrary notification entries (e.g., todo reminders)."""
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    if "message" not in entry:
        entry["message"] = "Notification triggered"
    logger.info("[Notification] %s", entry["message"])
    _append_entry(entry)
