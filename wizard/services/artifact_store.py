"""
Artifact Store
==============

Manages local installers, downloads, upgrades, and backups under memory/wizard.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from core.services.hash_utils import sha256_file
from core.services.json_utils import read_json_file, write_json_file
from core.services.time_utils import utc_now_iso
from wizard.services.path_utils import get_repo_root
from wizard.services.logging_api import get_logger

logger = get_logger("wizard-artifacts")


@dataclass
class ArtifactEntry:
    id: str
    kind: str  # installers|downloads|upgrades|backups
    filename: str
    size_bytes: int
    checksum: str
    created_at: str
    source_path: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class ArtifactStore:
    """Local artifact manager for Wizard-managed downloads/installers."""

    def __init__(self):
        root = get_repo_root() / "memory" / "wizard" / "artifacts"
        self.root = root
        self.index_path = root / "index.json"
        self.kinds = {
            "installers": root / "installers",
            "downloads": root / "downloads",
            "upgrades": root / "upgrades",
            "backups": root / "backups",
        }
        self._ensure_dirs()
        self._index = self._load_index()

    def _ensure_dirs(self):
        self.root.mkdir(parents=True, exist_ok=True)
        for path in self.kinds.values():
            path.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> Dict[str, ArtifactEntry]:
        data = read_json_file(self.index_path, default={})
        entries = {}
        for item in data.get("entries", []):
            entry = ArtifactEntry(**item)
            entries[entry.id] = entry
        return entries

    def _save_index(self) -> None:
        payload = {
            "updated_at": utc_now_iso(),
            "entries": [e.to_dict() for e in self._index.values()],
        }
        write_json_file(self.index_path, payload, indent=2)

    def _checksum(self, path: Path) -> str:
        return sha256_file(path, chunk_size=8192)

    def list(self, kind: Optional[str] = None) -> List[ArtifactEntry]:
        if kind and kind not in self.kinds:
            return []
        entries = list(self._index.values())
        if kind:
            entries = [e for e in entries if e.kind == kind]
        return sorted(entries, key=lambda e: e.created_at, reverse=True)

    def get(self, artifact_id: str) -> Optional[ArtifactEntry]:
        return self._index.get(artifact_id)

    def path_for(self, entry: ArtifactEntry) -> Path:
        return self.kinds.get(entry.kind, self.root) / entry.filename

    def add(self, source_path: Path, kind: str, notes: Optional[str] = None) -> ArtifactEntry:
        if kind not in self.kinds:
            raise ValueError(f"Unknown artifact kind: {kind}")
        if not source_path.exists():
            raise FileNotFoundError(str(source_path))

        target_dir = self.kinds[kind]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        dest_name = f"{timestamp}-{source_path.name}"
        dest_path = target_dir / dest_name
        shutil.copy2(source_path, dest_path)

        entry = ArtifactEntry(
            id=f"{kind}-{timestamp}-{source_path.stem}",
            kind=kind,
            filename=dest_path.name,
            size_bytes=dest_path.stat().st_size,
            checksum=self._checksum(dest_path),
            created_at=utc_now_iso(),
            source_path=str(source_path),
            notes=notes,
        )
        self._index[entry.id] = entry
        self._save_index()
        logger.info(f"[WIZ] Stored artifact {entry.id}")
        return entry

    def remove(self, artifact_id: str) -> bool:
        entry = self._index.get(artifact_id)
        if not entry:
            return False
        path = self.kinds.get(entry.kind, self.root) / entry.filename
        if path.exists():
            path.unlink()
        del self._index[artifact_id]
        self._save_index()
        return True


_artifact_store: Optional[ArtifactStore] = None


def get_artifact_store() -> ArtifactStore:
    global _artifact_store
    if _artifact_store is None:
        _artifact_store = ArtifactStore()
    return _artifact_store
