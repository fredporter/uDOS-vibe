"""Canonical version/build/artifact metadata resolvers for Sonic packaging."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import string

from core.services.packaging_manifest_service import load_packaging_manifest


def _global_manifest(repo_root: Path) -> dict[str, object]:
    manifest = load_packaging_manifest(repo_root)
    global_payload = manifest.get("global")
    if not isinstance(global_payload, dict):
        raise ValueError("packaging manifest missing global")
    return global_payload


def resolve_release_version(repo_root: Path) -> str:
    global_payload = _global_manifest(repo_root)
    version_source = global_payload.get("version_source")
    if not isinstance(version_source, dict):
        raise ValueError("global.version_source is required")

    path_value = version_source.get("path")
    priorities = version_source.get("field_priority")
    if not isinstance(path_value, str) or not path_value.strip():
        raise ValueError("global.version_source.path is required")
    if not isinstance(priorities, list) or not priorities:
        raise ValueError("global.version_source.field_priority is required")

    source_path = repo_root / path_value
    if not source_path.exists():
        raise FileNotFoundError(f"Missing version metadata: {source_path}")
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Version source must be object: {source_path}")

    for field in priorities:
        if not isinstance(field, str):
            continue
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if field == "version" and isinstance(value, dict):
            major = value.get("major")
            minor = value.get("minor")
            patch = value.get("patch")
            if all(isinstance(part, int) for part in (major, minor, patch)):
                return f"v{major}.{minor}.{patch}"

    raise ValueError(f"Unable to resolve release version from {source_path}")


def resolve_build_id(repo_root: Path, explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()

    global_payload = _global_manifest(repo_root)
    policy = global_payload.get("build_id_policy")
    if not isinstance(policy, dict):
        raise ValueError("global.build_id_policy is required")

    prefix = str(policy.get("prefix") or "").strip()
    timestamp_format = str(policy.get("timestamp_format") or "").strip()
    suffix_len = policy.get("random_suffix_length")
    if not prefix:
        raise ValueError("global.build_id_policy.prefix is required")
    if not timestamp_format:
        raise ValueError("global.build_id_policy.timestamp_format is required")
    if not isinstance(suffix_len, int) or suffix_len < 0:
        raise ValueError("global.build_id_policy.random_suffix_length must be >= 0")

    timestamp = datetime.now(timezone.utc).strftime(timestamp_format)
    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(suffix_len))
    return f"{prefix}-{timestamp}" if not suffix else f"{prefix}-{timestamp}-{suffix}"


def resolve_sonic_builds_root(repo_root: Path) -> Path:
    manifest = load_packaging_manifest(repo_root)
    platforms = manifest.get("platforms")
    if not isinstance(platforms, dict):
        raise ValueError("packaging manifest missing platforms")
    linux = platforms.get("linux")
    if not isinstance(linux, dict):
        raise ValueError("packaging manifest missing platforms.linux")
    app_bundle = linux.get("app_bundle")
    if not isinstance(app_bundle, dict):
        raise ValueError("packaging manifest missing platforms.linux.app_bundle")
    root = app_bundle.get("builds_root")
    if not isinstance(root, str) or not root.strip():
        raise ValueError("platforms.linux.app_bundle.builds_root is required")
    return repo_root / root


def _sanitize_artifact_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value)


def resolve_sonic_artifact_basename(repo_root: Path, build_id: str, version: str | None = None) -> str:
    resolved_version = version or resolve_release_version(repo_root)
    return f"sonic-stick-{_sanitize_artifact_segment(resolved_version)}-{build_id}"


def pick_sonic_build_dir(repo_root: Path, cli_build_dir: str | None = None) -> Path:
    if cli_build_dir:
        return Path(cli_build_dir).expanduser().resolve()

    builds_root = resolve_sonic_builds_root(repo_root)
    if not builds_root.exists():
        raise FileNotFoundError(f"Builds directory missing: {builds_root}")
    candidates = [item for item in builds_root.iterdir() if item.is_dir() and (item / "build-manifest.json").exists()]
    if not candidates:
        raise FileNotFoundError(f"No build directories with build-manifest.json under {builds_root}")
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0]
