"""Canonical JSON file helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

_T = TypeVar("_T")


def read_json_file(path: Path, *, default: _T) -> Any | _T:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json_file(path: Path, payload: Any, *, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=indent), encoding="utf-8")
