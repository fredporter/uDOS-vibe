from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.services.release_version_service import get_release_display_version


def test_release_version_prefers_display(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "version.json").write_text(
        json.dumps(
            {
                "display": "v9.9.9",
                "version": {"major": 1, "minor": 0, "patch": 0},
            }
        ),
        encoding="utf-8",
    )
    assert get_release_display_version(repo) == "v9.9.9"


def test_release_version_uses_semver_object_when_display_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "version.json").write_text(
        json.dumps({"version": {"major": 2, "minor": 4, "patch": 6}}),
        encoding="utf-8",
    )
    assert get_release_display_version(repo) == "v2.4.6"


def test_release_version_raises_when_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        get_release_display_version(repo)
