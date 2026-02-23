from __future__ import annotations

from pathlib import Path


def test_legacy_wrappers_removed():
    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / "distribution" / "plugins" / "api" / "server.py").exists()
    assert not (repo_root / "wizard" / "mcp" / "server.py").exists()
    assert not (repo_root / "wizard" / "services" / "sonic_service.py").exists()


def test_canonical_modular_entrypoints_exist():
    repo_root = Path(__file__).resolve().parents[2]
    assert (repo_root / "distribution" / "plugins" / "api" / "server_modular.py").exists()
    assert (repo_root / "wizard" / "mcp" / "mcp_server.py").exists()
    assert (repo_root / "wizard" / "services" / "sonic_plugin_service.py").exists()


def test_tui_legacy_module_removed():
    legacy_path = Path(__file__).resolve().parents[2] / "core" / "tui" / "ucode_legacy_main.py"
    assert not legacy_path.exists()
