"""Wizard key store compatibility wrapper.

Bridges legacy key-store calls to the unified secret store.
"""

from __future__ import annotations

import os
from typing import Optional

from wizard.services.secret_store import SecretStoreError, get_secret_store


_KEY_ID_MAP: dict[str, str] = {
    "MISTRAL_API_KEY": "mistral-api-key",
    "OPENROUTER_API_KEY": "openrouter-api-key",
    "OPENAI_API_KEY": "openai-api-key",
    "ANTHROPIC_API_KEY": "anthropic-api-key",
    "GEMINI_API_KEY": "gemini-api-key",
    "WIZARD_ADMIN_TOKEN": "wizard-admin-token",
}


def _resolve_key_id(key_name: str) -> str:
    normalized = key_name.strip().upper()
    if normalized in _KEY_ID_MAP:
        return _KEY_ID_MAP[normalized]
    return key_name.strip().lower().replace("_", "-")


def _unlock_store() -> Optional[object]:
    store = get_secret_store()
    try:
        store.unlock(os.getenv("WIZARD_KEY") or os.getenv("WIZARD_KEY_PEER"))
    except SecretStoreError:
        return None
    return store


def get_wizard_key(key_name: str) -> Optional[str]:
    """Get a wizard key from encrypted secret storage.

    Returns None when the secret store cannot be unlocked or the key is missing.
    """

    if not key_name.strip():
        return None
    store = _unlock_store()
    if store is None:
        return None
    key_id = _resolve_key_id(key_name)
    entry = store.get_entry(key_id)
    if entry is None:
        entry = store.get_entry(key_name)
    if entry is None:
        return None
    return entry.value


def set_wizard_key(key_name: str, key_value: str) -> bool:
    """Store a wizard key in encrypted secret storage."""

    if not key_name.strip() or not key_value:
        return False
    store = _unlock_store()
    if store is None:
        return False
    key_id = _resolve_key_id(key_name)
    store.set_entry(
        key_id=key_id,
        value=key_value,
        metadata={"source": "wizard.security.key_store"},
        provider="wizard_key_store",
    )
    return True
