from __future__ import annotations

import json
from pathlib import Path

from core.services.packaging_build_metadata_service import (
    pick_sonic_build_dir,
    resolve_build_id,
    resolve_release_version,
    resolve_sonic_artifact_basename,
    resolve_sonic_builds_root,
)


def test_resolve_release_version_uses_manifest_source(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "version.json").write_text(json.dumps({"display": "v8.8.8"}), encoding="utf-8")
    assert resolve_release_version(repo) == "v8.8.8"


def test_resolve_build_id_honors_explicit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    assert resolve_build_id(repo, explicit="custom-build") == "custom-build"


def test_resolve_sonic_artifact_basename_sanitizes_version(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    value = resolve_sonic_artifact_basename(repo, build_id="b1", version="v1.0.0+meta")
    assert value == "sonic-stick-v1.0.0-meta-b1"


def test_pick_sonic_build_dir_uses_manifest_builds_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    build_dir = repo / "distribution" / "builds" / "abc"
    build_dir.mkdir(parents=True)
    (repo / "version.json").write_text(json.dumps({"display": "v1.0.0"}), encoding="utf-8")
    (build_dir / "build-manifest.json").write_text("{}", encoding="utf-8")

    assert resolve_sonic_builds_root(repo) == repo / "distribution" / "builds"
    assert pick_sonic_build_dir(repo).name == "abc"
