#!/usr/bin/env python3
"""Phase 4 DB backup/restore sanity check."""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


TABLES = ["records", "events", "sources", "tasks", "companies", "contact_companies"]


def _counts(db_path: Path) -> Dict[str, int]:
    with sqlite3.connect(str(db_path)) as conn:
        out: Dict[str, int] = {}
        for table in TABLES:
            out[table] = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        return out


def _integrity(db_path: Path) -> str:
    with sqlite3.connect(str(db_path)) as conn:
        return conn.execute("PRAGMA integrity_check").fetchone()[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="SQLite backup/restore sanity")
    parser.add_argument("--db", default="data/empire.db")
    parser.add_argument("--backup-dir", default="data/backups")
    parser.add_argument("--restore-dir", default="data/restore-check")
    args = parser.parse_args()

    source_db = Path(args.db)
    if not source_db.exists():
        print(f"FAIL source DB missing: {source_db}")
        return 1

    backup_dir = Path(args.backup_dir)
    restore_dir = Path(args.restore_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    restore_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_db = backup_dir / f"empire-{stamp}.db"
    restore_db = restore_dir / f"restore-{stamp}.db"

    source_counts = _counts(source_db)

    with sqlite3.connect(str(source_db)) as src_conn, sqlite3.connect(str(backup_db)) as dst_conn:
        src_conn.backup(dst_conn)

    shutil.copy2(backup_db, restore_db)
    restore_counts = _counts(restore_db)
    integrity = _integrity(restore_db)

    if source_counts != restore_counts:
        print(f"FAIL count mismatch source={source_counts} restore={restore_counts}")
        return 1
    if integrity.lower() != "ok":
        print(f"FAIL integrity_check={integrity}")
        return 1

    print(f"PASS backup={backup_db}")
    print(f"PASS restore={restore_db}")
    print(f"PASS counts={restore_counts}")
    print("PASS integrity_check=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
