"""
Dev State Helper
================

Lightweight helper to reflect Wizard DEV mode state in local TUI.
Uses a short TTL cache to avoid spamming the Wizard API.
"""

from __future__ import annotations

import os
import time
from urllib.parse import urlparse
from typing import Optional

from core.services.stdlib_http import http_get, HTTPError

_CACHE_ACTIVE: Optional[bool] = None
_CACHE_TS: float = 0.0
_CACHE_TTL = 2.0
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


def _loopback_wizard_base_url(raw_base_url: str) -> str:
    candidate = (raw_base_url or "").strip().rstrip("/") or "http://localhost:8765"
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").strip().lower()
    if host in _LOOPBACK_HOSTS:
        return candidate
    return "http://localhost:8765"


def _env_dev_active() -> Optional[bool]:
    raw = os.getenv("UDOS_DEV_MODE")
    if raw is None:
        return None
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_dev_active(force: bool = False, ttl: float = _CACHE_TTL) -> Optional[bool]:
    global _CACHE_ACTIVE, _CACHE_TS
    now = time.time()
    if not force and _CACHE_ACTIVE is not None and (now - _CACHE_TS) < ttl:
        return _CACHE_ACTIVE

    base_url = _loopback_wizard_base_url(os.getenv("WIZARD_BASE_URL", "http://localhost:8765"))
    admin_token = os.getenv("WIZARD_ADMIN_TOKEN")
    if not admin_token:
        active = _env_dev_active()
        _CACHE_ACTIVE = active
        _CACHE_TS = now
        return active

    try:
        resp = http_get(
            f"{base_url}/api/dev/status",
            headers={"X-Admin-Token": admin_token},
            timeout=1,
        )
        if resp.get("status_code") == 200:
            data = resp.get("json") or {}
            active = bool(data.get("active"))
            os.environ["UDOS_DEV_MODE"] = "1" if active else "0"
        else:
            active = _env_dev_active()
    except HTTPError:
        active = _env_dev_active()

    _CACHE_ACTIVE = active
    _CACHE_TS = now
    return active


def get_dev_state_label() -> str:
    active = get_dev_active()
    return "ON" if active else "OFF"
