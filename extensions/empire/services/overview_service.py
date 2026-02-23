"""Overview data for Empire UI."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Any

from empire.services.storage import DEFAULT_DB_PATH, ensure_schema


def _fetch_one(conn: sqlite3.Connection, query: str) -> int:
    row = conn.execute(query).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def load_overview(db_path: Path = DEFAULT_DB_PATH, *, event_limit: int = 6) -> Dict[str, Any]:
    ensure_schema(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        total_records = _fetch_one(conn, "SELECT COUNT(*) FROM records")
        total_sources = _fetch_one(conn, "SELECT COUNT(*) FROM sources")
        total_events = _fetch_one(conn, "SELECT COUNT(*) FROM events")

        events: List[Dict[str, Any]] = []
        for row in conn.execute(
            "SELECT event_type, occurred_at, subject, notes FROM events ORDER BY occurred_at DESC LIMIT ?",
            (event_limit,),
        ):
            events.append(
                {
                    "type": row["event_type"],
                    "occurred_at": row["occurred_at"],
                    "subject": row["subject"],
                    "notes": row["notes"],
                }
            )

    return {
        "counts": {
            "records": total_records,
            "sources": total_sources,
            "events": total_events,
        },
        "events": events,
    }
