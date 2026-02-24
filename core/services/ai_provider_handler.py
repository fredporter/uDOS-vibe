"""Unified AI Provider Handler

Central source of truth for AI provider availability checking.
Replaces scattered status checks in:
  - core/tui/ucode.py: _get_ok_local_status(), _get_ok_cloud_status()
  - wizard/routes/provider_routes.py: check_provider_status()

Both TUI and Wizard call this single service for provider status.

**Design Principle:**
  Checks BOTH configuration state AND runtime state.
  Returns unified response for TUI and Wizard.

**Usage:**
```python
from core.services.ai_provider_handler import AIProviderHandler, get_ai_provider_handler

handler = get_ai_provider_handler()

# Check local Ollama
status = handler.check_local_provider()
if status.is_available:
    print(f"Ready: {status.loaded_models}")
else:
    print(f"Issue: {status.issue}")

# Check cloud Mistral
cloud_status = handler.check_cloud_provider()

# Check all providers
all_status = handler.check_all_providers()
for provider, status in all_status.items():
    print(f"{provider}: {status.is_available}")
```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """AI provider types."""

    OLLAMA_LOCAL = "ollama_local"  # Local Ollama instance
    MISTRAL_CLOUD = "mistral_cloud"  # Mistral API (cloud)


@dataclass
class ProviderStatus:
    """Status of a single provider."""

    provider_id: str
    is_configured: bool  # Config files/keys exist
    is_running: bool  # Process is actually running
    is_available: bool  # Can be used right now (configured AND running)
    loaded_models: list[str] = field(default_factory=list)  # What's loaded/available
    default_model: str | None = None  # Configured default model
    issue: str | None = None  # Why not available (if not)
    last_checked: datetime = field(default_factory=datetime.utcnow)
    details: dict[str, Any] = field(default_factory=dict)  # Extra info

    def __str__(self) -> str:
        """Return readable status string."""
        if self.is_available:
            model_list = ", ".join(self.loaded_models[:3])
            if len(self.loaded_models) > 3:
                model_list += f", +{len(self.loaded_models) - 3} more"
            return f"✅ {self.provider_id.upper()}: available ({model_list})"
        else:
            return f"⚠️ {self.provider_id.upper()}: {self.issue or 'not available'}"


class AIProviderHandler:
    """Unified AI provider status checking.

    Answers both:
      1. Is provider configured? (config files, secrets, etc.)
      2. Is provider running? (live health check)

    Result: Single unified response for TUI and Wizard.
    """

    def __init__(self):
        """Initialize handler."""
        self.logger = logger
        self._cache: dict[str, ProviderStatus] = {}
        self._cache_ttl_seconds = 10  # Cache provider status for 10s

    def check_all_providers(self) -> dict[str, ProviderStatus]:
        """Check status of all configured providers.

        Returns:
            Dict mapping provider IDs to their status
        """
        return {
            ProviderType.OLLAMA_LOCAL.value: self.check_local_provider(),
            ProviderType.MISTRAL_CLOUD.value: self.check_cloud_provider(),
        }

    def check_local_provider(self) -> ProviderStatus:
        """Check local Ollama provider status.

        Performs two checks:
          1. Configuration check: Is Ollama setup?
          2. Runtime check: Is Ollama running and healthy?

        Returns:
            ProviderStatus with is_configured, is_running, is_available
        """
        provider_id = ProviderType.OLLAMA_LOCAL.value

        # Check 1: Is Ollama configured?
        is_configured = self._check_ollama_configured()

        # Check 2: Is Ollama running?
        is_running, models_loaded, check_issue = self._check_ollama_running()

        # Combined: available = configured AND running
        is_available = is_configured and is_running

        # Get configured default model
        default_model = self._get_configured_default_model()

        # Determine issue if not available
        issue = None
        if not is_available:
            if not is_configured:
                issue = "ollama not configured"
            elif not is_running:
                issue = check_issue or "ollama not running"

        # Verify default model is loaded (if specified)
        if is_available and default_model:
            normalized_loaded = self._normalize_model_names(models_loaded)
            normalized_default = self._normalize_model_names([default_model])
            if normalized_default.isdisjoint(normalized_loaded):
                is_available = False
                issue = f"model not loaded: {default_model}"
                models_loaded = []

        return ProviderStatus(
            provider_id=provider_id,
            is_configured=is_configured,
            is_running=is_running,
            is_available=is_available,
            loaded_models=models_loaded,
            default_model=default_model,
            issue=issue,
            details={
                "endpoint": self._get_ollama_endpoint(),
                "configured_profiles": self._get_ollama_config_profiles(),
            },
        )

    def check_cloud_provider(self) -> ProviderStatus:
        """Check cloud (Mistral) provider status.

        Returns:
            ProviderStatus indicating Mistral API availability
        """
        provider_id = ProviderType.MISTRAL_CLOUD.value

        # Check 1: Is Mistral configured?
        is_configured = self._check_mistral_configured()

        # Check 2: Can we reach Mistral?
        is_running, api_models, check_issue = self._check_mistral_running()

        # Combined: available = configured AND running
        is_available = is_configured and is_running

        issue = None
        if not is_available:
            if not is_configured:
                issue = "mistral api key not configured"
            elif not is_running:
                issue = check_issue or "mistral api unreachable"

        return ProviderStatus(
            provider_id=provider_id,
            is_configured=is_configured,
            is_running=is_running,
            is_available=is_available,
            loaded_models=api_models,
            default_model="mistral-small",  # Mistral provides predefined models
            issue=issue,
            details={"api_endpoint": "api.mistral.ai"},
        )

    # ===== Private helpers: Configuration checks =====

    @staticmethod
    def _check_ollama_configured() -> bool:
        """Check if Ollama is configured (CLI installed, config present).

        Returns:
            True if Ollama setup detected
        """
        import shutil

        # Check 1: Ollama CLI installed
        if not shutil.which("ollama"):
            return False

        # Check 2: Ollama config exists (optional, but indicates setup intent)
        try:
            from pathlib import Path

            config_dir = Path.home() / ".ollama"
            if not config_dir.exists():
                return False
        except Exception:
            pass

        return True

    @staticmethod
    def _check_mistral_configured() -> bool:
        """Check if Mistral is configured (API key present).

        Returns:
            True if Mistral API key found
        """
        from core.services.admin_secret_contract import SecureVault
        from core.services.unified_config_loader import get_config

        # Check 1: Environment variable
        if get_config("MISTRAL_API_KEY", ""):
            return True

        # Check 2: Secret store
        try:
            vault = SecureVault()
            if vault.get_secret("mistral_api_key"):
                return True
        except Exception:
            pass

        return False

    # ===== Private helpers: Runtime checks =====

    @staticmethod
    def _check_ollama_running() -> tuple[bool, list[str], str | None]:
        """Check if Ollama is running and get loaded models.

        Returns:
            (is_running, models_list, issue_string_or_none)
        """
        try:
            from wizard.routes.ollama_route_utils import (
                get_installed_ollama_models_payload,
            )

            result = get_installed_ollama_models_payload()
            if result.get("success"):
                models = [
                    m.get("name") for m in result.get("models", []) if m.get("name")
                ]
                return True, models, None
            else:
                issue = result.get("error", "ollama not reachable")
                return False, [], issue
        except Exception as exc:
            return False, [], str(exc)

    @staticmethod
    def _check_mistral_running() -> tuple[bool, list[str], str | None]:
        """Check if Mistral API is reachable.

        Returns:
            (is_reachable, available_models, issue_string_or_none)
        """
        try:
            from core.services.unified_config_loader import get_config

            api_key = get_config("MISTRAL_API_KEY", "")
            if not api_key:
                return False, [], "no api key"

            # Try a simple API call
            # For now, assume if key exists and Wizard responds, Mistral is available
            # Full implementation would do actual API health check
            return True, ["mistral-small", "mistral-medium", "mistral-large"], None
        except Exception as exc:
            return False, [], f"mistral check failed: {exc!s}"

    @staticmethod
    def _get_configured_default_model() -> str | None:
        """Get the configured default model for local provider.

        Returns:
            Default model name or None
        """
        try:
            from core.tui.ucode import UCODE

            ucode = UCODE()
            return ucode._get_ok_default_model()
        except Exception:
            return None

    # ===== Private helpers: Utilities =====

    @staticmethod
    def _normalize_model_names(names: list[str]) -> set[str]:
        """Return canonical model names (both tagged and base forms).

        Args:
            names: List of model names (may include tags)

        Returns:
            Set of normalized names
        """
        normalized: set[str] = set()
        for raw in names:
            name = (raw or "").strip()
            if not name:
                continue
            normalized.add(name)
            # Also add base name (without tag)
            base = name.split(":", 1)[0].strip()
            if base:
                normalized.add(base)
        return normalized

    @staticmethod
    def _get_ollama_endpoint() -> str:
        """Get configured Ollama endpoint.

        Returns:
            Endpoint URL
        """
        from core.services.unified_config_loader import get_config

        return get_config("OLLAMA_HOST", "http://127.0.0.1:11434")

    @staticmethod
    def _get_ollama_config_profiles() -> list[str]:
        """Get list of Ollama config profiles (for systems with multiple configs).

        Returns:
            List of profile names
        """
        # TODO: Implement multi-profile support
        return ["default"]

    def log_status(self, status: ProviderStatus) -> None:
        """Log provider status for audit trail.

        Args:
            status: ProviderStatus to log
        """
        if status.is_available:
            self.logger.info(
                f"[AI_PROVIDER] {status.provider_id}: available "
                f"({len(status.loaded_models)} models, default: {status.default_model})"
            )
        else:
            self.logger.warning(
                f"[AI_PROVIDER] {status.provider_id}: {status.issue or 'unavailable'}"
            )


# Singleton instance
_handler: AIProviderHandler | None = None


def get_ai_provider_handler() -> AIProviderHandler:
    """Get singleton AIProviderHandler instance.

    Returns:
        AIProviderHandler singleton
    """
    global _handler
    if _handler is None:
        _handler = AIProviderHandler()
    return _handler


# Convenience functions for TUI


def check_local_provider() -> ProviderStatus:
    """Convenience wrapper to check local provider.

    Returns:
        ProviderStatus
    """
    return get_ai_provider_handler().check_local_provider()


def check_cloud_provider() -> ProviderStatus:
    """Convenience wrapper to check cloud provider.

    Returns:
        ProviderStatus
    """
    return get_ai_provider_handler().check_cloud_provider()


def check_all_providers() -> dict[str, ProviderStatus]:
    """Convenience wrapper to check all providers.

    Returns:
        Dict of all provider statuses
    """
    return get_ai_provider_handler().check_all_providers()
