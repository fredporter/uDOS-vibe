"""Dedupe helpers for Empire records."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Optional

from empire.services.normalization_service import NormalizedRecord


def _norm(value: Optional[str]) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _email_key(email: Optional[str]) -> str:
    if not email:
        return ""
    return email.strip().lower()


def dedupe_key(record: NormalizedRecord) -> str:
    email = _email_key(record.email)
    name = _norm(record.name)
    org = _norm(record.organization)
    if email:
        return f"email:{email}"
    if name and org:
        return f"name_org:{name}|{org}"
    if name:
        return f"name:{name}"
    return f"source:{record.source}|id:{record.record_id}"


def fuzzy_match(a: Optional[str], b: Optional[str], threshold: float = 0.88) -> bool:
    if not a or not b:
        return False
    score = SequenceMatcher(a=_norm(a), b=_norm(b)).ratio()
    return score >= threshold


def name_org_match(
    name_a: Optional[str],
    org_a: Optional[str],
    name_b: Optional[str],
    org_b: Optional[str],
    *,
    threshold: float = 0.88,
) -> bool:
    if not name_a or not name_b:
        return False
    name_ok = fuzzy_match(name_a, name_b, threshold=threshold)
    if not org_a or not org_b:
        return name_ok
    org_ok = fuzzy_match(org_a, org_b, threshold=threshold)
    return name_ok and org_ok
