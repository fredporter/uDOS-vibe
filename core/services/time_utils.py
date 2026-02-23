"""Canonical time helpers for UTC timestamps."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return timezone-aware UTC ISO timestamp."""
    return datetime.now(timezone.utc).isoformat()


def utc_now_iso_z() -> str:
    """Return UTC ISO timestamp with Z suffix and no microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
