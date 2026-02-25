from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.time_utils import utc_now_iso
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard", category="provider-load", name="provider-load")


def _get_log_path() -> Path:
    logs_dir = get_repo_root() / "memory" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / "provider-load.log"


def log_provider_event(
    provider: str,
    status: str,
    reason: str,
    source: str = "quota-tracker",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Append a provider load entry for automation."""
    entry = {
        "timestamp": utc_now_iso(),
        "provider": provider,
        "status": status,
        "reason": reason,
        "source": source,
        "metadata": metadata or {},
    }
    path = _get_log_path()
    with open(path, "a") as fh:
        fh.write(json.dumps(entry) + "\n")
    logger.event(
        "info",
        "provider.load",
        f"[PROVIDER] Logged {status} for {provider}: {reason}",
        ctx=entry,
    )


def read_recent_provider_events(limit: int = 10) -> List[Dict[str, Any]]:
    """Read the most recent provider load entries."""
    path = _get_log_path()
    if not path.exists():
        return []

    lines = path.read_text().strip().splitlines()
    events = []
    for line in reversed(lines[-limit:]):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events
