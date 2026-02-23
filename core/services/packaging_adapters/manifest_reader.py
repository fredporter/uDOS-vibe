"""Single manifest read helper for packaging adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.packaging_manifest_service import load_packaging_manifest


def read_manifest(repo_root: Path) -> dict[str, Any]:
    return load_packaging_manifest(repo_root)


def read_platform(repo_root: Path, platform: str) -> dict[str, Any]:
    manifest = read_manifest(repo_root)
    platforms = manifest.get("platforms")
    if not isinstance(platforms, dict):
        raise ValueError("packaging manifest missing platforms object")
    payload = platforms.get(platform)
    if not isinstance(payload, dict):
        raise ValueError(f"packaging manifest missing platform config: {platform}")
    return payload
