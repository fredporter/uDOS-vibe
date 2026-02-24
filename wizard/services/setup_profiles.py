"""Setup Profiles (Wizard)
=======================

Secure storage for user + installation profiles via secret store.
Installation metrics (moves) are tracked in memory/wizard.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import secrets
from typing import Any

from core.services.unified_config_loader import get_config
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_memory_dir, get_repo_root
from wizard.services.secret_store import SecretEntry, SecretStoreError, get_secret_store

logger = get_logger("setup-profiles")

USER_PROFILE_KEY_ID = "wizard-user-profile"
INSTALL_PROFILE_KEY_ID = "wizard-install-profile"


@dataclass
class ProfileResult:
    data: dict[str, Any] | None
    locked: bool = False
    error: str | None = None


def _write_env_var(env_path: Path, key: str, value: str) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if env_path.exists():
        lines = env_path.read_text().splitlines()
    updated = False
    new_lines = []
    for line in lines:
        if not line or line.strip().startswith("#") or "=" not in line:
            new_lines.append(line)
            continue
        k, _ = line.split("=", 1)
        if k.strip() == key:
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    env_path.write_text("\n".join(new_lines) + "\n")


def _ensure_wizard_key() -> str:
    existing = get_config("WIZARD_KEY", "")
    if existing:
        return existing
    key = secrets.token_urlsafe(32)
    env_path = get_repo_root() / ".env"
    _write_env_var(env_path, "WIZARD_KEY", key)
    os.environ["WIZARD_KEY"] = key
    return key


def _unlock_store() -> tuple[Any | None, str | None]:
    try:
        store = get_secret_store()
        store.unlock()
        return store, None
    except SecretStoreError as exc:
        return None, str(exc)


def _store_profile(key_id: str, payload: dict[str, Any]) -> ProfileResult:
    _ensure_wizard_key()
    store, error = _unlock_store()
    if not store:
        return ProfileResult(data=None, locked=True, error=error)
    entry = SecretEntry(
        key_id=key_id,
        provider="wizard_setup",
        value=json.dumps(payload, sort_keys=True),
        created_at=datetime.now(UTC).isoformat(),
        metadata={"source": "wizard-setup"},
    )
    try:
        store.set(entry)
    except SecretStoreError as exc:
        return ProfileResult(data=None, locked=True, error=str(exc))
    return ProfileResult(data=payload)


def _load_profile(key_id: str) -> ProfileResult:
    store, error = _unlock_store()
    if not store:
        return ProfileResult(data=None, locked=True, error=error)
    try:
        entry = store.get(key_id)
    except SecretStoreError as exc:
        return ProfileResult(data=None, locked=True, error=str(exc))
    if not entry or not entry.value:
        return ProfileResult(data=None)
    try:
        data = json.loads(entry.value)
    except json.JSONDecodeError:
        data = {"raw": entry.value}
    return ProfileResult(data=data)


def save_user_profile(profile: dict[str, Any]) -> ProfileResult:
    profile = {**profile}
    profile.setdefault("updated_at", datetime.now(UTC).isoformat())
    profile.setdefault("created_at", profile.get("updated_at"))
    return _store_profile(USER_PROFILE_KEY_ID, profile)


def save_install_profile(profile: dict[str, Any]) -> ProfileResult:
    profile = {**profile}
    profile.setdefault("updated_at", datetime.now(UTC).isoformat())
    profile.setdefault("created_at", profile.get("updated_at"))
    if not profile.get("installation_id"):
        existing = load_install_profile()
        if existing.data and existing.data.get("installation_id"):
            profile["installation_id"] = existing.data.get("installation_id")
        else:
            profile["installation_id"] = f"udos-{secrets.token_hex(8)}"
    return _store_profile(INSTALL_PROFILE_KEY_ID, profile)


def load_user_profile() -> ProfileResult:
    return _load_profile(USER_PROFILE_KEY_ID)


def load_install_profile() -> ProfileResult:
    return _load_profile(INSTALL_PROFILE_KEY_ID)


def _metrics_path() -> Path:
    return get_memory_dir() / "wizard" / "installation-metrics.json"


def load_install_metrics() -> dict[str, Any]:
    path = _metrics_path()
    if not path.exists():
        return {
            "moves_used": 0,
            "moves_limit": None,
            "lifespan_mode": "infinite",
            "created_at": datetime.now(UTC).isoformat(),
            "last_move_at": None,
        }
    try:
        return json.loads(path.read_text())
    except Exception:
        return {
            "moves_used": 0,
            "moves_limit": None,
            "lifespan_mode": "infinite",
            "created_at": datetime.now(UTC).isoformat(),
            "last_move_at": None,
        }


def save_install_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    path = _metrics_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2))
    return metrics


def sync_metrics_from_profile(install_profile: dict[str, Any]) -> dict[str, Any]:
    metrics = load_install_metrics()
    lifespan = install_profile.get("lifespan", {})
    mode = lifespan.get("mode") or install_profile.get("lifespan_mode") or "infinite"
    moves_limit = lifespan.get("moves_limit", install_profile.get("moves_limit"))
    metrics["lifespan_mode"] = mode
    metrics["moves_limit"] = moves_limit if moves_limit not in ("", None) else None
    return save_install_metrics(metrics)


def increment_moves(count: int = 1) -> dict[str, Any]:
    metrics = load_install_metrics()
    metrics["moves_used"] = int(metrics.get("moves_used") or 0) + count
    metrics["last_move_at"] = datetime.now(UTC).isoformat()
    return save_install_metrics(metrics)
