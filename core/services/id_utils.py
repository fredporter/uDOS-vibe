"""Canonical runtime ID helpers for session/job/correlation IDs."""

from __future__ import annotations

import secrets


def generate_runtime_id(prefix: str, *, size: int = 8) -> str:
    """Return a stable prefixed runtime identifier."""
    token = secrets.token_urlsafe(size)
    return f"{prefix}-{token}"

