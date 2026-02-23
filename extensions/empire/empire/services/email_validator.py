"""Email validation utilities for Empire."""

from __future__ import annotations

import re
from typing import Dict


ROLE_BASED_PREFIXES = {
    "admin",
    "billing",
    "careers",
    "contact",
    "customerservice",
    "hello",
    "help",
    "info",
    "jobs",
    "press",
    "sales",
    "security",
    "support",
}

BOT_PREFIXES = {
    "no-reply",
    "noreply",
    "do-not-reply",
    "donotreply",
    "auto-reply",
    "autoreply",
    "autoresponder",
    "mailer-daemon",
    "postmaster",
}


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email(address: str) -> Dict[str, object]:
    address = (address or "").strip().lower()
    result = {
        "valid": False,
        "reason": "empty",
        "role_based": False,
        "bot_like": False,
    }

    if not address:
        return result

    if not EMAIL_RE.match(address):
        result["reason"] = "format"
        return result

    local = address.split("@")[0]
    local_clean = local.replace(".", "").replace("-", "")
    result["role_based"] = local_clean in ROLE_BASED_PREFIXES
    result["bot_like"] = local in BOT_PREFIXES or local_clean in BOT_PREFIXES

    if result["bot_like"]:
        result["reason"] = "bot"
        return result

    result["valid"] = True
    result["reason"] = "ok"
    return result
