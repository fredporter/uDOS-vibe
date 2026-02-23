"""Manifest-backed offline assets path contract resolver."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.services.packaging_manifest_service import load_packaging_manifest


@dataclass(frozen=True)
class OfflineAssetsContract:
    root: Path
    cache_namespace: Path


def resolve_offline_assets_contract(repo_root: Path) -> OfflineAssetsContract:
    manifest = load_packaging_manifest(repo_root)
    global_payload = manifest.get("global")
    if not isinstance(global_payload, dict):
        raise ValueError("packaging manifest missing global")
    offline = global_payload.get("offline_assets")
    if not isinstance(offline, dict):
        raise ValueError("packaging manifest missing global.offline_assets")

    raw_root = offline.get("root")
    raw_cache = offline.get("cache_namespace")
    if not isinstance(raw_root, str) or not raw_root.strip():
        raise ValueError("global.offline_assets.root is required")
    if not isinstance(raw_cache, str) or not raw_cache.strip():
        raise ValueError("global.offline_assets.cache_namespace is required")

    return OfflineAssetsContract(
        root=repo_root / raw_root,
        cache_namespace=repo_root / raw_cache,
    )
