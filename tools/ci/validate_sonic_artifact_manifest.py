#!/usr/bin/env python3
"""Validate Sonic build-manifest.json and checksums.txt emitted by build-sonic-stick.sh."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from core.services.packaging_build_metadata_service import (
    pick_sonic_build_dir,
    resolve_sonic_artifact_basename,
)


REQUIRED_TOP_LEVEL = {
    "schema",
    "build_id",
    "created_at",
    "profile",
    "version",
    "repository",
    "artifacts",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksums(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Malformed checksum line: {line!r}")
        rows[parts[-1]] = parts[0]
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", help="Build output directory to validate")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    build_dir = pick_sonic_build_dir(repo_root, cli_build_dir=args.build_dir)

    manifest_path = build_dir / "build-manifest.json"
    checksums_path = build_dir / "checksums.txt"

    if not manifest_path.exists():
        print(f"[sonic-artifacts] FAIL: missing {manifest_path}")
        return 1
    if not checksums_path.exists():
        print(f"[sonic-artifacts] FAIL: missing {checksums_path}")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[sonic-artifacts] FAIL: invalid JSON manifest: {exc}")
        return 1

    missing = sorted(REQUIRED_TOP_LEVEL - set(manifest.keys()))
    if missing:
        print(f"[sonic-artifacts] FAIL: manifest missing fields: {', '.join(missing)}")
        return 1

    repo = manifest.get("repository") or {}
    if not repo.get("root_sha"):
        print("[sonic-artifacts] FAIL: repository.root_sha missing")
        return 1
    if not repo.get("sonic_sha"):
        print("[sonic-artifacts] FAIL: repository.sonic_sha missing")
        return 1

    artifacts = manifest.get("artifacts") or []
    if not isinstance(artifacts, list) or not artifacts:
        print("[sonic-artifacts] FAIL: artifacts must be a non-empty list")
        return 1
    expected_basename = resolve_sonic_artifact_basename(
        repo_root,
        build_id=str(manifest.get("build_id")),
        version=str(manifest.get("version")),
    )

    expected_files = set()
    for entry in artifacts:
        rel = entry.get("path")
        declared_hash = entry.get("sha256")
        declared_size = entry.get("size_bytes")
        if not rel or not declared_hash:
            print(f"[sonic-artifacts] FAIL: artifact missing path/sha256: {entry}")
            return 1
        path = build_dir / rel
        if not path.exists():
            print(f"[sonic-artifacts] FAIL: artifact path not found: {path}")
            return 1
        if not path.name.startswith(expected_basename):
            print(f"[sonic-artifacts] FAIL: artifact name mismatch for naming policy: {path.name}")
            return 1
        actual_hash = sha256(path)
        if actual_hash != declared_hash:
            print(f"[sonic-artifacts] FAIL: sha256 mismatch for {rel}")
            return 1
        if not isinstance(declared_size, int) or path.stat().st_size != declared_size:
            print(f"[sonic-artifacts] FAIL: size mismatch for {rel}")
            return 1
        expected_files.add(path.name)

    checksum_rows = parse_checksums(checksums_path)
    for filename in sorted(expected_files | {manifest_path.name}):
        path = build_dir / filename
        if filename not in checksum_rows:
            print(f"[sonic-artifacts] FAIL: missing checksum row for {filename}")
            return 1
        if checksum_rows[filename] != sha256(path):
            print(f"[sonic-artifacts] FAIL: checksum mismatch in checksums.txt for {filename}")
            return 1

    print(f"[sonic-artifacts] PASS: validated {build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
