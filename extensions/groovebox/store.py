"""Groovebox pattern store (library-level, UI-agnostic)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\s_-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-") or "pattern"


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "uDOS.py").exists():
            return parent
    return Path.cwd()


@dataclass
class GrooveboxPatternSummary:
    pattern_id: str
    name: str
    tempo: Optional[int]
    updated_at: Optional[str]
    created_at: Optional[str]
    track_count: int


class GrooveboxStore:
    """Persist Groovebox patterns in memory/groovebox."""

    def __init__(self, memory_root: Optional[Path] = None):
        repo_root = _find_repo_root()
        self.memory_root = memory_root or (repo_root / "memory")
        self.pattern_root = self.memory_root / "groovebox" / "patterns"
        self.pattern_root.mkdir(parents=True, exist_ok=True)

    def _pattern_path(self, pattern_id: str) -> Path:
        return self.pattern_root / f"{pattern_id}.json"

    def list_patterns(self) -> List[Dict[str, Any]]:
        patterns: List[Dict[str, Any]] = []
        if not self.pattern_root.exists():
            return patterns
        for path in sorted(self.pattern_root.glob("*.json")):
            try:
                payload = json.loads(path.read_text())
            except Exception:
                continue
            pattern_id = payload.get("id") or path.stem
            tracks = payload.get("tracks") or []
            summary = GrooveboxPatternSummary(
                pattern_id=str(pattern_id),
                name=str(payload.get("name") or payload.get("title") or pattern_id),
                tempo=payload.get("tempo"),
                updated_at=payload.get("updated_at"),
                created_at=payload.get("created_at"),
                track_count=len(tracks),
            )
            patterns.append(summary.__dict__)
        return patterns

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        path = self._pattern_path(pattern_id)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text())
        except Exception:
            return None
        payload.setdefault("id", pattern_id)
        return payload

    def save_pattern(
        self,
        pattern: Dict[str, Any],
        pattern_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not isinstance(pattern, dict):
            raise ValueError("Pattern payload must be an object")
        name = str(pattern.get("name") or pattern.get("title") or "Untitled")
        pattern_id = pattern_id or pattern.get("id") or _slugify(name)
        now = datetime.utcnow().isoformat()

        existing = self.get_pattern(str(pattern_id))
        stored: Dict[str, Any] = dict(pattern)
        stored["id"] = str(pattern_id)
        stored["name"] = name
        stored.setdefault("tempo", 120)
        stored.setdefault("meta", {})
        stored.setdefault("tracks", [])
        stored["source"] = source or stored.get("source") or "manual"
        stored["updated_at"] = now
        stored.setdefault("created_at", existing.get("created_at") if existing else now)

        path = self._pattern_path(str(pattern_id))
        path.write_text(json.dumps(stored, indent=2, sort_keys=True))
        return stored


def get_groovebox_store() -> GrooveboxStore:
    return GrooveboxStore()
