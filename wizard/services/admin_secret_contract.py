"""Wizard admin token/key/secret-store contract checks and repair helpers."""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wizard.services.path_utils import get_repo_root
from wizard.services.secret_store import SecretEntry, SecretStoreError, get_secret_store
from wizard.services.wizard_config import load_wizard_config_data, save_wizard_config_data
from core.services.unified_config_loader import get_config

DEFAULT_ADMIN_KEY_ID = "wizard-admin-token"


def _read_env_vars(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _write_env_var(env_path: Path, key: str, value: str) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    out: list[str] = []
    updated = False
    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in line:
            out.append(line)
            continue
        line_key, _ = line.split("=", 1)
        if line_key.strip() == key:
            out.append(f"{key}={value}")
            updated = True
            continue
        out.append(line)
    if not updated:
        out.append(f"{key}={value}")
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _seed_admin_secret(
    *,
    admin_key_id: str,
    wizard_key: str,
    admin_token: str,
) -> None:
    store = get_secret_store()
    store.unlock(wizard_key)
    store.set(
        SecretEntry(
            key_id=admin_key_id,
            provider="wizard-admin",
            value=admin_token,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"source": "admin-secret-contract-repair"},
        )
    )


def _hard_reset_locked_secret_store(root: Path, admin_key_id: str) -> tuple[str, str]:
    tomb_path = root / "wizard" / "secrets.tomb"
    key_path = root / "memory" / "bank" / "private" / "wizard_secret_store.key"
    key_path.parent.mkdir(parents=True, exist_ok=True)

    wizard_key = secrets.token_urlsafe(48)
    admin_token = secrets.token_urlsafe(48)

    if tomb_path.exists():
        tomb_path.unlink()

    key_path.write_text(wizard_key, encoding="utf-8")
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        pass

    if hasattr(get_secret_store, "_instance"):
        delattr(get_secret_store, "_instance")

    _seed_admin_secret(
        admin_key_id=admin_key_id,
        wizard_key=wizard_key,
        admin_token=admin_token,
    )
    return wizard_key, admin_token


def collect_admin_secret_contract(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or get_repo_root()
    env_path = root / ".env"
    config_path = root / "wizard" / "config" / "wizard.json"

    env_values = _read_env_vars(env_path)
    wizard_key = env_values.get("WIZARD_KEY") or get_config("WIZARD_KEY", "").strip()
    admin_token = env_values.get("WIZARD_ADMIN_TOKEN") or get_config(
        "WIZARD_ADMIN_TOKEN", ""
    ).strip()

    config = load_wizard_config_data(path=config_path)
    admin_key_id = str(config.get("admin_api_key_id") or "").strip()
    effective_key_id = admin_key_id or DEFAULT_ADMIN_KEY_ID

    secret_entry_value = ""
    secret_entry_present = False
    secret_store_locked = False
    lock_error = ""

    try:
        store = get_secret_store()
        store.unlock(wizard_key or None)
        entry = store.get_entry(effective_key_id)
        if entry and entry.value:
            secret_entry_present = True
            secret_entry_value = entry.value.strip()
    except SecretStoreError as exc:
        secret_store_locked = True
        lock_error = str(exc)

    drift: list[str] = []
    if not wizard_key:
        drift.append("missing_wizard_key")
    if not admin_key_id:
        drift.append("missing_admin_api_key_id")
    if not admin_token:
        drift.append("missing_admin_token")
    if secret_store_locked:
        drift.append("secret_store_locked")
    elif not secret_entry_present:
        drift.append("missing_secret_entry")
    elif admin_token and secret_entry_value != admin_token:
        drift.append("token_mismatch")

    repair_actions: list[str] = []
    if "missing_wizard_key" in drift:
        repair_actions.append("generate_wizard_key")
    if "missing_admin_api_key_id" in drift:
        repair_actions.append("set_admin_api_key_id")
    if "missing_admin_token" in drift:
        repair_actions.append(
            "sync_admin_token_from_secret"
            if secret_entry_present
            else "generate_admin_token"
        )
    if "missing_secret_entry" in drift or "token_mismatch" in drift:
        repair_actions.append("sync_secret_from_admin_token")
    if "secret_store_locked" in drift:
        repair_actions.append("repair_secret_store_tomb")

    return {
        "ok": not drift,
        "drift": _unique(drift),
        "repair_actions": _unique(repair_actions),
        "env_path": str(env_path),
        "config_path": str(config_path),
        "admin_api_key_id": admin_key_id or None,
        "effective_admin_api_key_id": effective_key_id,
        "wizard_key_present": bool(wizard_key),
        "admin_token_present": bool(admin_token),
        "secret_store_locked": secret_store_locked,
        "secret_store_error": lock_error or None,
        "secret_entry_present": secret_entry_present,
        "token_match": bool(admin_token and secret_entry_value == admin_token),
    }


def repair_admin_secret_contract(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or get_repo_root()
    env_path = root / ".env"
    config_path = root / "wizard" / "config" / "wizard.json"

    status_before = collect_admin_secret_contract(repo_root=root)
    env_values = _read_env_vars(env_path)
    config = load_wizard_config_data(path=config_path)

    wizard_key = env_values.get("WIZARD_KEY") or get_config("WIZARD_KEY", "").strip()
    if not wizard_key:
        wizard_key = secrets.token_urlsafe(48)

    admin_key_id = str(config.get("admin_api_key_id") or "").strip() or DEFAULT_ADMIN_KEY_ID
    config["admin_api_key_id"] = admin_key_id
    save_wizard_config_data(config, path=config_path)

    existing_token = (
        env_values.get("WIZARD_ADMIN_TOKEN")
        or get_config("WIZARD_ADMIN_TOKEN", "").strip()
    )

    secret_value = ""
    try:
        store = get_secret_store()
        store.unlock(wizard_key)
        entry = store.get_entry(admin_key_id)
        if entry and entry.value:
            secret_value = entry.value.strip()
    except SecretStoreError as exc:
        wizard_key, admin_token = _hard_reset_locked_secret_store(root, admin_key_id)
        _write_env_var(env_path, "WIZARD_KEY", wizard_key)
        _write_env_var(env_path, "WIZARD_ADMIN_TOKEN", admin_token)
        os.environ["WIZARD_KEY"] = wizard_key
        os.environ["WIZARD_ADMIN_TOKEN"] = admin_token
        status_after = collect_admin_secret_contract(repo_root=root)
        return {
            "status": "repaired" if status_after["ok"] else "partial",
            "repaired": bool(status_after["ok"]),
            "recovery_mode": "secret_store_reset",
            "message": f"Secret store unlock failed and was reset: {exc}",
            "status_before": status_before,
            "status_after": status_after,
        }

    admin_token = existing_token or secret_value or secrets.token_urlsafe(48)
    _write_env_var(env_path, "WIZARD_KEY", wizard_key)
    _write_env_var(env_path, "WIZARD_ADMIN_TOKEN", admin_token)
    os.environ["WIZARD_KEY"] = wizard_key
    os.environ["WIZARD_ADMIN_TOKEN"] = admin_token

    _seed_admin_secret(
        admin_key_id=admin_key_id,
        wizard_key=wizard_key,
        admin_token=admin_token,
    )

    status_after = collect_admin_secret_contract(repo_root=root)
    return {
        "status": "repaired" if status_after["ok"] else "partial",
        "repaired": bool(status_after["ok"]),
        "status_before": status_before,
        "status_after": status_after,
    }
