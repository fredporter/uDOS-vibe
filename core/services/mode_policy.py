"""Runtime mode policy for Ghost/User/Dev behavior."""

from __future__ import annotations

from enum import StrEnum
import os

from core.services.dev_state import get_dev_active
from core.services.user_service import Permission, get_user_manager, is_ghost_mode
from core.services.wizard_mode_state import get_wizard_mode_active


class RuntimeMode(StrEnum):
    """Runtime persona mode."""

    GHOST = "ghost"
    USER = "user"
    WIZARD = "wizard"
    DEV = "dev"


def resolve_runtime_mode() -> RuntimeMode:
    """Resolve active runtime mode."""
    if is_ghost_mode():
        return RuntimeMode.GHOST

    user_manager = get_user_manager()
    dev_active = bool(get_dev_active())
    can_dev = user_manager.has_permission(Permission.DEV_MODE)
    if dev_active and can_dev:
        return RuntimeMode.DEV

    wizard_active = bool(get_wizard_mode_active())
    can_wizard_admin = user_manager.has_permission(Permission.ADMIN)
    if wizard_active and can_wizard_admin:
        return RuntimeMode.WIZARD

    return RuntimeMode.USER


def boundaries_enforced() -> bool:
    """Return True when mode boundaries should be hard-enforced."""
    raw = os.environ.get("UDOS_ENFORCE_MODE_BOUNDARIES", "").strip().lower()
    if raw in {"0", "false", "no", "off"}:
        return False
    if raw in {"1", "true", "yes", "on"}:
        return True
    return True


def mode_summary() -> dict[str, str]:
    """Return mode summary with policy rationale."""
    mode = resolve_runtime_mode()
    match mode:
        case RuntimeMode.GHOST:
            return {
                "mode": mode.value,
                "label": "Ghost Mode",
                "purpose": "Safe first-run/demo and recovery mode",
                "policy": "Read-only core protections with guided educational flow",
            }
        case RuntimeMode.DEV:
            return {
                "mode": mode.value,
                "label": "Dev Mode",
                "purpose": "Contributor/admin mode for core and extension development",
                "policy": "Full development access with explicit admin + dev activation",
            }
        case RuntimeMode.WIZARD:
            return {
                "mode": mode.value,
                "label": "Wizard Mode",
                "purpose": "Admin operations mode for packaging/distribution and platform control",
                "policy": "Elevated admin operations without core/extension contribution permissions",
            }
        case RuntimeMode.USER:
            return {
                "mode": mode.value,
                "label": "User Mode",
                "purpose": "Daily productivity and wellness usage",
                "policy": "Restrict non-essential coding/tech scope to protect runtime UX",
            }


def user_mode_scope_flag(prompt: str) -> str | None:
    """Return a policy flag message for USER mode prompts outside scope."""
    if resolve_runtime_mode() is not RuntimeMode.USER:
        return None

    normalized = prompt.lower()
    if not normalized.strip():
        return None

    sonic_terms = {
        "sonic",
        "device",
        "usb",
        "payload",
        "driver",
        "compatibility",
        "hardware",
        "flash",
        "firmware",
    }
    if any(term in normalized for term in sonic_terms):
        return None

    external_tech_terms = {
        "kubernetes",
        "terraform",
        "aws",
        "gcp",
        "azure",
        "docker compose",
        "kafka",
        "postgres tuning",
        "redis cluster",
        "microservice",
        "ci/cd",
        "react app",
        "typescript framework",
    }
    if any(term in normalized for term in external_tech_terms):
        return "user_mode_scope"
    return None


def should_block_user_mode_prompt(prompt: str) -> bool:
    """Compatibility wrapper for old call sites."""
    return user_mode_scope_flag(prompt) is not None and boundaries_enforced()
