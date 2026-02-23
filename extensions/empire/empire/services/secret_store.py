"""Secret storage for Empire (private-only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
KEY_FILE = CONFIG_DIR / ".empire_key"
SECRETS_FILE = CONFIG_DIR / "empire_secrets.json"

try:
    from cryptography.fernet import Fernet

    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False


def _load_key() -> Optional[bytes]:
    if not KEY_FILE.exists():
        if not CRYPTO_AVAILABLE:
            return None
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        return key
    return KEY_FILE.read_bytes()


def _load_secrets() -> Dict[str, str]:
    if not SECRETS_FILE.exists():
        return {}
    try:
        return json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_secrets(payload: Dict[str, str]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SECRETS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def set_secret(key: str, value: str) -> None:
    secrets = _load_secrets()
    if CRYPTO_AVAILABLE:
        key_bytes = _load_key()
        if key_bytes:
            cipher = Fernet(key_bytes)
            secrets[key] = cipher.encrypt(value.encode("utf-8")).decode("utf-8")
        else:
            secrets[key] = value
    else:
        secrets[key] = value
    _save_secrets(secrets)


def get_secret(key: str) -> Optional[str]:
    secrets = _load_secrets()
    value = secrets.get(key)
    if value is None:
        return None
    if not CRYPTO_AVAILABLE:
        return value
    key_bytes = _load_key()
    if not key_bytes:
        return value
    try:
        cipher = Fernet(key_bytes)
        return cipher.decrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return value
