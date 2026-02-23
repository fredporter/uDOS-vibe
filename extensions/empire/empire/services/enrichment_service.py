"""Enrichment hooks for Empire records."""

from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from empire.services.normalization_service import NormalizedRecord

EnrichmentHook = Callable[["NormalizedRecord"], "NormalizedRecord"]

_HOOKS: List[EnrichmentHook] = []


def register_hook(hook: EnrichmentHook) -> None:
    _HOOKS.append(hook)


def clear_hooks() -> None:
    _HOOKS.clear()


def apply_hooks(record: "NormalizedRecord") -> "NormalizedRecord":
    for hook in _HOOKS:
        record = hook(record)
    return record


def _normalize_company_suffix(record: "NormalizedRecord") -> "NormalizedRecord":
    if not record.organization:
        return record
    organization = record.organization.replace(" Inc.", " Inc").replace(" LLC", " LLC").strip()
    record.organization = organization
    return record


register_hook(_normalize_company_suffix)
