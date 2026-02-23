"""Dependency profile resolver and renderers for packaging surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.packaging_manifest_service import load_packaging_manifest


def _platform_manifest(repo_root: Path, platform: str) -> dict[str, Any]:
    manifest = load_packaging_manifest(repo_root)
    platforms = manifest.get("platforms")
    if not isinstance(platforms, dict):
        raise ValueError("packaging manifest missing platforms")
    payload = platforms.get(platform)
    if not isinstance(payload, dict):
        raise ValueError(f"packaging manifest missing platform '{platform}'")
    return payload


def default_dependency_profile(repo_root: Path, platform: str) -> str:
    payload = _platform_manifest(repo_root, platform)
    profile = payload.get("default_dependency_profile")
    if not isinstance(profile, str) or not profile.strip():
        raise ValueError(f"{platform}.default_dependency_profile is required")
    return profile


def dependency_profile(repo_root: Path, platform: str, profile: str | None = None) -> dict[str, list[str]]:
    payload = _platform_manifest(repo_root, platform)
    profiles = payload.get("dependency_profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"{platform}.dependency_profiles is required")
    selected = profile or default_dependency_profile(repo_root, platform)
    entry = profiles.get(selected)
    if not isinstance(entry, dict):
        raise ValueError(f"missing dependency profile '{selected}' for platform '{platform}'")
    runtime = entry.get("runtime_packages")
    build = entry.get("build_packages")
    if not isinstance(runtime, list) or not isinstance(build, list):
        raise ValueError(f"invalid dependency profile '{selected}' for platform '{platform}'")
    return {
        "runtime_packages": [str(item) for item in runtime if isinstance(item, str) and item.strip()],
        "build_packages": [str(item) for item in build if isinstance(item, str) and item.strip()],
    }


def render_apkbuild_dependency_snippet(repo_root: Path, profile: str = "udos-ui-thin-gui") -> str:
    deps = dependency_profile(repo_root, "linux", profile)

    def _render_list(name: str, values: list[str]) -> str:
        rows = [f'{name}="']
        rows.extend(f"    {item}" for item in values)
        rows.append('"')
        return "\n".join(rows)

    header = (
        "# Generated from packaging.manifest.json\n"
        f"# source: platforms.linux.dependency_profiles.{profile}\n"
    )
    return "\n".join(
        [
            header.rstrip(),
            _render_list("depends", deps["runtime_packages"]),
            "",
            _render_list("makedepends", deps["build_packages"]),
            "",
        ]
    )


def render_dependency_docs_table(repo_root: Path) -> str:
    manifest = load_packaging_manifest(repo_root)
    platforms = manifest.get("platforms")
    if not isinstance(platforms, dict):
        raise ValueError("packaging manifest missing platforms")

    lines = [
        "# Packaging Dependency Map",
        "",
        "Generated from `packaging.manifest.json` dependency profiles.",
        "",
        "| Platform | Profile | Runtime Packages | Build Packages |",
        "| --- | --- | --- | --- |",
    ]
    for platform in ("linux", "windows", "macos"):
        platform_payload = platforms.get(platform)
        if not isinstance(platform_payload, dict):
            continue
        profiles = platform_payload.get("dependency_profiles")
        if not isinstance(profiles, dict):
            continue
        for profile in sorted(profiles):
            deps = dependency_profile(repo_root, platform, profile)
            runtime = ", ".join(deps["runtime_packages"]) or "-"
            build = ", ".join(deps["build_packages"]) or "-"
            lines.append(f"| {platform} | `{profile}` | {runtime} | {build} |")
    lines.append("")
    return "\n".join(lines)
