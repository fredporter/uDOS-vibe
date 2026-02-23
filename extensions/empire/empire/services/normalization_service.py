"""Record normalization utilities for Empire."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional

from empire.services.enrichment_service import apply_hooks
from empire.services.email_validator import validate_email


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NormalizedRecord:
    record_id: str
    source: str
    normalized_at: str
    name: Optional[str]
    organization: Optional[str]
    role: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    raw: Dict[str, object]


def _slug(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return " ".join(value.split())


def _email(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.strip().lower()


def _hash_record(source: str, name: Optional[str], email: Optional[str]) -> str:
    payload = f"{source}|{name or ''}|{email or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _extract(raw: Dict[str, object], *keys: str) -> Optional[str]:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def normalize_payload(source: str, raw: Dict[str, object]) -> NormalizedRecord:
    name = _slug(_extract(raw, "name", "full_name", "fullName"))
    organization = _slug(_extract(raw, "organization", "org", "company"))
    role = _slug(_extract(raw, "role", "title", "position"))
    email = _email(_extract(raw, "email", "email_address"))
    if email:
        validation = validate_email(email)
        if not validation["valid"] and not validation["role_based"]:
            email = None
    phone = _slug(_extract(raw, "phone", "phone_number", "phoneNumber"))
    record_id = _hash_record(source, name, email)
    record = NormalizedRecord(
        record_id=record_id,
        source=source,
        normalized_at=_utc_now(),
        name=name,
        organization=organization,
        role=role,
        email=email,
        phone=phone,
        raw=raw,
    )
    return apply_hooks(record)


def iter_normalized(input_path: Path) -> Iterable[NormalizedRecord]:
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            source = str(payload.get("source") or "unknown")
            raw = payload.get("payload")
            if isinstance(raw, dict):
                yield normalize_payload(source, raw)


def write_normalized(
    input_path: Path,
    output_path: Path,
    *,
    persist: bool = True,
    db_path: Optional[Path] = None,
) -> int:
    from empire.services.storage import upsert_record, DEFAULT_DB_PATH, record_event

    resolved_db_path = db_path or DEFAULT_DB_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for record in iter_normalized(input_path):
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            if persist:
                upsert_record(record, db_path=resolved_db_path)
            count += 1
    if persist:
        record_event(
            record_id=None,
            event_type="normalize",
            occurred_at=_utc_now(),
            subject=f"Normalized {count} records",
            notes=str(input_path),
            db_path=resolved_db_path,
        )
    return count
