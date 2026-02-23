"""Shared compact status formatter for one-line HUD outputs."""

from __future__ import annotations

from typing import Any


def format_compact_status(
    prefix: str,
    fields: dict[str, Any],
    *,
    order: list[str] | None = None,
) -> str:
    """Format a compact status line with stable ordering."""
    raw_prefix = str(prefix).strip() or "STATUS"
    label = raw_prefix if (raw_prefix.endswith(":") or ":" in raw_prefix) else f"{raw_prefix}:"
    keys = order[:] if order else sorted(fields.keys())
    chunks: list[str] = [label]
    for key in keys:
        if key not in fields:
            continue
        value = fields.get(key)
        if value is None:
            continue
        text = str(value).replace("|", "/").strip()
        if not text:
            continue
        chunks.append(f"{key}={text}")
    return " | ".join(chunks)
