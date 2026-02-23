"""Email processing scaffolding for Empire."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from empire.services.normalization_service import NormalizedRecord, normalize_payload
from empire.services.storage import (
    upsert_record,
    ensure_schema,
    DEFAULT_DB_PATH,
    record_event,
    record_task,
    task_exists_by_source,
)


@dataclass
class EmailTask:
    title: str
    category: str
    source: str
    source_ref: str
    created_at: str
    notes: str
    record_id: str | None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _category(subject: str, body: str) -> str:
    haystack = f"{subject} {body}".lower()
    if any(word in haystack for word in ["invoice", "payment", "receipt"]):
        return "finance"
    if any(word in haystack for word in ["meeting", "call", "schedule"]):
        return "meeting"
    if any(word in haystack for word in ["issue", "support", "bug"]):
        return "support"
    return "general"


def _extract_email(sender: str) -> str:
    match = re.search(r"[\w\.-]+@[\w\.-]+", sender)
    return match.group(0) if match else ""


def _extract_name(sender: str) -> str:
    name = sender.split("<")[0].strip().strip("\"")
    return name if name else ""


def process_emails(
    emails: List[Dict[str, str]],
    *,
    db_path=DEFAULT_DB_PATH,
) -> Dict[str, List]:
    ensure_schema(db_path)
    tasks: List[EmailTask] = []
    records: List[NormalizedRecord] = []

    for message in emails:
        subject = message.get("subject", "")
        body = message.get("body", "")
        sender = message.get("from", "")
        message_id = message.get("message_id") or message.get("id") or ""
        source = f"email:{message_id}" if message_id else f"email:{sender}"
        category = _category(subject, body)

        if message_id and task_exists_by_source(source, db_path=db_path):
            continue

        raw = {
            "name": _extract_name(sender),
            "email": _extract_email(sender),
            "title": None,
            "company": None,
        }
        record = normalize_payload("email", raw)
        records.append(record)
        record_id = None
        if record.email or record.name:
            record_id = upsert_record(record, db_path=db_path)

        task = EmailTask(
            title=subject or "Email follow-up",
            category=category,
            source=source,
            source_ref=sender,
            created_at=_utc_now(),
            notes=(body[:240] + "...") if len(body) > 240 else body,
            record_id=record_id,
        )
        tasks.append(task)
        record_task(
            title=task.title,
            category=task.category,
            source=task.source,
            source_ref=task.source_ref,
            created_at=task.created_at,
            status="open",
            notes=task.notes,
            record_id=task.record_id,
            dedupe_by_source=bool(message_id),
            db_path=db_path,
        )

    record_event(
        record_id=None,
        event_type="email.process",
        occurred_at=_utc_now(),
        subject=f"Processed {len(emails)} emails",
        notes="email pipeline",
        db_path=db_path,
    )

    return {
        "tasks": tasks,
        "records": records,
    }
