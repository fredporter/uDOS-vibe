"""Raw data ingestion utilities for Empire."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from empire.services.storage import DEFAULT_DB_PATH, record_event, record_source


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl"}


@dataclass
class IngestionRecord:
    source: str
    ingested_at: str
    payload: Dict[str, object]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iter_csv(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def _iter_json(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        yield data


def _iter_jsonl(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                yield item


def iter_payloads(path: Path) -> Iterable[Dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    if path.suffix.lower() == ".csv":
        return _iter_csv(path)
    if path.suffix.lower() == ".json":
        return _iter_json(path)
    if path.suffix.lower() == ".jsonl":
        return _iter_jsonl(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def ingest_file(
    input_path: Path,
    output_path: Path,
    *,
    source_label: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Ingest a file and write raw records to JSONL."""
    source = source_label or input_path.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for payload in iter_payloads(input_path):
            record = IngestionRecord(
                source=source,
                ingested_at=_utc_now(),
                payload=payload,
            )
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            count += 1
    record_source(source, label=source, created_at=_utc_now(), db_path=db_path)
    record_event(
        record_id=None,
        event_type="ingest",
        occurred_at=_utc_now(),
        subject=f"Ingested {count} records",
        notes=str(input_path),
        db_path=db_path,
    )
    return count


def ingest_many(
    inputs: List[Path],
    output_path: Path,
    *,
    source_label: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Ingest multiple files into a single JSONL output."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for input_path in inputs:
            source = source_label or input_path.name
            for payload in iter_payloads(input_path):
                record = IngestionRecord(
                    source=source,
                    ingested_at=_utc_now(),
                    payload=payload,
                )
                handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
                count += 1
            record_source(source, label=source, created_at=_utc_now(), db_path=db_path)
            record_event(
                record_id=None,
                event_type="ingest",
                occurred_at=_utc_now(),
                subject=f"Ingested {source}",
                notes=str(input_path),
                db_path=db_path,
            )
    return count
