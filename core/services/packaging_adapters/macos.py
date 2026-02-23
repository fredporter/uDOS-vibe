"""macOS packaging adapter executor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.packaging_adapters.manifest_reader import read_platform


def config(repo_root: Path) -> dict[str, Any]:
    return dict(read_platform(repo_root, "macos"))
