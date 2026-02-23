"""Canonical release version resolver for packaging/build surfaces."""

from __future__ import annotations

from pathlib import Path

from core.services.packaging_build_metadata_service import resolve_release_version


def get_release_display_version(repo_root: Path) -> str:
    """Resolve release display version from packaging manifest version source.

    Raises:
        FileNotFoundError: if configured version source file is missing.
        ValueError: if no usable version fields exist.
    """
    return resolve_release_version(repo_root)
