#!/usr/bin/env python3
"""CLI entry for Empire record normalization."""

from __future__ import annotations

import argparse
from pathlib import Path

from empire.services.normalization_service import write_normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize raw JSONL records")
    parser.add_argument("--in", dest="input_path", required=True, help="Raw JSONL path")
    parser.add_argument("--out", required=True, help="Normalized JSONL path")
    parser.add_argument("--db", default=None, help="Optional SQLite DB path")
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Skip persisting normalized records to DB",
    )
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    count = write_normalized(
        Path(args.input_path),
        Path(args.out),
        persist=not args.no_persist,
        db_path=db_path if db_path else None,
    )
    print(f"Normalized {count} records -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
