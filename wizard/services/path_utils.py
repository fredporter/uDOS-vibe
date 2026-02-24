from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.path_service import (
    find_repo_root as _find_repo_root,
    get_repo_root as _get_repo_root,
)
from core.services.unified_config_loader import get_config
from wizard.services.wizard_config import load_wizard_config_data


def find_repo_root(start_path: Path | None = None) -> Path:
    return _find_repo_root(start_path=start_path, marker="uDOS.py")


def get_memory_dir() -> Path:
    """Get memory/ directory path (creates if doesn't exist)."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    memory_root = locations.get("memory_root", "memory")
    memory_dir = _resolve_repo_path(memory_root)
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def get_vault_dir() -> Path:
    """Get vault directory path (creates if doesn't exist)."""
    env_root = get_config("VAULT_ROOT")
    if env_root:
        vault_dir = Path(env_root).expanduser()
        if not vault_dir.is_absolute():
            vault_dir = get_repo_root() / vault_dir
    else:
        vault_dir = get_repo_root() / "memory" / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


def get_distribution_dir() -> Path:
    """Get distribution/ directory path (creates if doesn't exist)."""
    dist_dir = find_repo_root() / "distribution"
    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir


def get_logs_dir() -> Path:
    """Get memory/logs/ directory path (creates if doesn't exist)."""
    logs_dir = get_memory_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_artifacts_dir() -> Path:
    """Get .artifacts/ directory path (creates if doesn't exist)."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = (
        get_config("UDOS_ARTIFACTS_ROOT")
        or locations.get("artifacts_root")
        or ".artifacts"
    )
    artifacts_dir = _resolve_repo_path(configured)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir


def get_test_runs_dir() -> Path:
    """Get test run artifacts directory (creates if doesn't exist)."""
    config = _load_wizard_config()
    locations = config.get("file_locations", {}) if isinstance(config, dict) else {}
    configured = (
        get_config("UDOS_TEST_RUNS_ROOT")
        or locations.get("test_runs_root")
        or str(Path(".artifacts") / "test-runs")
    )
    test_runs_dir = _resolve_repo_path(configured)
    test_runs_dir.mkdir(parents=True, exist_ok=True)
    return test_runs_dir


def _resolve_venv_path(raw_path: str) -> Path:
    """Resolve venv path from env/user input, allowing relative paths."""
    return _resolve_repo_path(raw_path)


def _resolve_repo_path(raw_path: str) -> Path:
    """Resolve path from env/config input, allowing relative repo paths."""
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = get_repo_root() / candidate
    return candidate


def get_wizard_venv_dir() -> Path:
    """Return Wizard runtime venv path.

    Priority:
    1. WIZARD_VENV_PATH env (absolute or repo-relative)
    2. Default repo path: venv
    """
    env_venv = get_config("WIZARD_VENV_PATH", "").strip()
    if env_venv:
        return _resolve_venv_path(env_venv)

    return get_repo_root() / "venv"


def get_repo_root() -> Path:
    """Get cached repo root using canonical path service."""
    return _get_repo_root(marker="uDOS.py")


def _load_wizard_config() -> dict[str, Any]:
    """Load wizard.json config if available."""
    return load_wizard_config_data()
