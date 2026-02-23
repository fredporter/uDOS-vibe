"""Wizard mode state management."""

from __future__ import annotations

import json
import os
from pathlib import Path

from core.services.logging_api import get_repo_root

_ENABLED_VALUES = {"1", "true", "yes", "on"}


def _state_path() -> Path:
    return Path(get_repo_root()) / "memory" / "system" / "wizard_mode_state.json"


def get_wizard_mode_active() -> bool:
    """Return True if wizard mode is enabled."""
    env_value = os.getenv("UDOS_WIZARD_MODE", "").strip().lower()
    if env_value:
        return env_value in _ENABLED_VALUES

    path = _state_path()
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool(payload.get("active"))


def set_wizard_mode_active(active: bool) -> bool:
    """Persist and export wizard mode state."""
    normalized = bool(active)
    os.environ["UDOS_WIZARD_MODE"] = "1" if normalized else "0"
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"active": normalized}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return normalized
