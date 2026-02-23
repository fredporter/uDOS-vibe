"""Repo structure boundary checks for Milestone 2.1."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_boundary_core_runtime_surfaces_exist() -> None:
    assert (REPO_ROOT / "core" / "commands").is_dir()
    assert (REPO_ROOT / "core" / "services").is_dir()
    assert (REPO_ROOT / "core" / "tui").is_dir()


def test_boundary_wizard_mcp_gateway_is_canonical() -> None:
    assert (REPO_ROOT / "wizard" / "mcp" / "mcp_server.py").is_file()
    assert (REPO_ROOT / "wizard" / "mcp" / "gateway.py").is_file()

    # Guard against accidental duplicate MCP entrypoints in core/extensions.
    assert not (REPO_ROOT / "core" / "mcp").exists()
    assert not (REPO_ROOT / "extensions" / "mcp").exists()


def test_boundary_extensions_module_surface_exists() -> None:
    extensions_dir = REPO_ROOT / "extensions"
    assert extensions_dir.is_dir()
    extension_packages = [entry for entry in extensions_dir.iterdir() if entry.is_dir() and not entry.name.startswith(".")]
    assert extension_packages
