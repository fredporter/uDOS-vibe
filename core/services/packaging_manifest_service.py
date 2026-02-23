"""Strict packaging manifest v2 loader and validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.services.packaging_manifest_models import PackagingManifestV2

DEFAULT_PACKAGING_MANIFEST: dict[str, Any] = PackagingManifestV2().model_dump(by_alias=True)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def load_packaging_manifest(repo_root: Path) -> dict[str, Any]:
    """Load strict v2 packaging manifest with defaults + validation."""
    manifest_path = repo_root / "packaging.manifest.json"
    overlay: dict[str, Any]
    if not manifest_path.exists():
        overlay = {}
    else:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("packaging.manifest.json must be a JSON object")
        overlay = payload
    merged = _deep_merge(DEFAULT_PACKAGING_MANIFEST, overlay)
    return PackagingManifestV2.model_validate(merged).model_dump(by_alias=True)
