"""Dependency profile contracts for Core vs Wizard separation."""

from __future__ import annotations

from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _contains_package(entries: list[str], package_name: str) -> bool:
    return any(entry.split(">=")[0].split("==")[0].strip() == package_name for entry in entries)


def test_fastapi_is_not_in_core_base_dependencies() -> None:
    root = _load_toml(REPO_ROOT / "pyproject.toml")
    udos = _load_toml(REPO_ROOT / "pyproject.udos.toml")

    root_dependencies = root["project"]["dependencies"]
    udos_dependencies = udos["project"]["dependencies"]

    assert not _contains_package(root_dependencies, "fastapi")
    assert not _contains_package(udos_dependencies, "fastapi")


def test_fastapi_is_in_wizard_dependency_profiles() -> None:
    root = _load_toml(REPO_ROOT / "pyproject.toml")
    udos = _load_toml(REPO_ROOT / "pyproject.udos.toml")

    root_wizard_dependencies = root["project"]["optional-dependencies"]["udos-wizard"]
    udos_wizard_dependencies = udos["project"]["optional-dependencies"]["wizard"]

    assert _contains_package(root_wizard_dependencies, "fastapi")
    assert _contains_package(udos_wizard_dependencies, "fastapi")
