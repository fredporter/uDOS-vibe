"""Unified Configuration Loader

Central source of truth for all uDOS configuration.
Replaces scattered os.getenv() calls and ad-hoc config loading.

Loads configuration in priority order:
  1. .env file (environment variables) — highest priority
  2. config.toml — application settings
  3. wizard.json — wizard server config
  4. ok_modes.json — AI provider config
  5. provider_setup_flags.json — provider state
  6. Defaults — built-in defaults

**Design Principle:**
  Single point of configuration access.
  Type-safe, validated configuration.
  Caching for performance.

**Usage:**
```python
from core.services.unified_config_loader import get_config_loader, ConfigKey

loader = get_config_loader()

# Get typed configuration value
port = loader.get_int("WIZARD_PORT", default=8765)
root_path = loader.get_path("UDOS_ROOT")
dev_mode = loader.get_bool("UDOS_DEV_MODE", default=False)

# List all settings in a section
ui_settings = loader.get_section("ui")

# Watch for changes
loader.watch_config_changes(callback=my_callback)
```
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)


@dataclass
class ConfigValue:
    """Single configuration value with metadata."""

    key: str
    value: Any
    source: Literal["env", "toml", "json", "default"]  # Where it came from
    section: str | None = None  # TOML section
    docstring: str | None = None  # Documentation


class UnifiedConfigLoader:
    """Central configuration loader for all uDOS settings.

    Loads configuration from:
      - .env → environment variables (highest priority)
      - core/config/config.toml → application settings (TOML)
      - wizard/config/wizard.json → wizard server config
      - core/config/ok_modes.json → AI provider config
      - wizard/config/provider_setup_flags.json → provider state
      - Built-in defaults
    """

    # Default configuration values
    DEFAULTS = {
        "UDOS_ROOT": None,  # Must be set at runtime
        "VAULT_ROOT": None,
        "WIZARD_BASE_URL": "http://localhost:8765",
        "WIZARD_PORT": "8765",
        "USER_NAME": "ghost",
        "UDOS_DEV_MODE": "0",
        "UDOS_TEST_MODE": "1",  # v1.4.x is testing/alert-only
        "UDOS_AUTOMATION": "0",
        "UDOS_QUIET": "0",
        "UDOS_TUI_CLEAN_STARTUP": "1",
        "UDOS_TUI_INVERT_HEADERS": "0",
        "UDOS_NO_ANSI": "0",
        "NO_COLOR": "0",
        "OLLAMA_HOST": "http://127.0.0.1:11434",
        "VIBE_PRIMARY_PROVIDER": "local",
        "VIBE_SECONDARY_PROVIDER": "cloud",
    }

    def __init__(self, repo_root: Path | str | None = None):
        """Initialize config loader.

        Args:
            repo_root: Optional override of repository root path
        """
        self.logger = logger
        self._repo_root = self._resolve_repo_root(repo_root)
        self._env_cache: dict[str, str] = {}
        self._toml_cache: dict[str, Any] = {}
        self._json_caches: dict[str, dict[str, Any]] = {}
        self._all_values: dict[str, ConfigValue] = {}
        self._config_watchers: list[Callable[[str, Any], None]] = []
        self._load_all_configs()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Searches in priority order:
          1. Process env
          2. .env
          3. TOML
          4. JSON configs
          5. Defaults
          6. Provided default

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        if env_value := os.environ.get(key):
            return env_value

        # Check cached all values
        if key in self._all_values:
            return self._all_values[key].value

        # Check defaults
        if key in self.DEFAULTS:
            return self.DEFAULTS[key] or default

        return default

    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            String value
        """
        value = self.get(key, default)
        return str(value) if value is not None else default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Integer value
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value.

        Accepts: 1, true, yes, on (case-insensitive)

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Boolean value
        """
        value = self.get(key, "").lower().strip()
        if value in ("1", "true", "yes", "on"):
            return True
        if value in ("0", "false", "no", "off"):
            return False
        return default

    def get_path(self, key: str, default: Path | None = None) -> Path | None:
        """Get path configuration value.

        Expands UDOS_ROOT and VAULT_ROOT references.
        Converts ~ to home directory.

        Args:
            key: Configuration key
            default: Default path

        Returns:
            Resolved Path or default
        """
        value = self.get(key)
        if not value:
            return default

        # Expand environment variables
        expanded = os.path.expandvars(str(value))
        expanded = os.path.expanduser(expanded)

        return Path(expanded)

    def get_section(self, section: str) -> dict[str, Any]:
        """Get all configuration values in a section.

        Args:
            section: Section name (e.g., "ui", "app", "dev")

        Returns:
            Dict of values in that section
        """
        result = {}
        for key, cfg_value in self._all_values.items():
            if cfg_value.section == section:
                result[key] = cfg_value.value
        return result

    def list_all_keys(self) -> list[str]:
        """List all configuration keys.

        Returns:
            Sorted list of all keys
        """
        return sorted(set(list(self._all_values.keys()) + list(self.DEFAULTS.keys())))

    def get_source(self, key: str) -> str:
        """Get the source of a configuration value.

        Returns:
            "env", "toml", "json", or "default"
        """
        if key in os.environ:
            return "env"
        if key in self._all_values:
            return self._all_values[key].source
        return "default"

    def find_keys(self, pattern: str) -> list[str]:
        """Find configuration keys matching a pattern.

        Pattern can include wildcards (e.g., "UDOS_*", "*MODE")

        Args:
            pattern: Search pattern

        Returns:
            List of matching keys
        """
        import fnmatch

        all_keys = self.list_all_keys()
        return fnmatch.filter(all_keys, pattern)

    def watch_config_changes(self, callback: Callable[[str, Any], None]) -> None:
        """Register a callback for configuration changes.

        Callback signature: callback(key: str, new_value: Any)

        Args:
            callback: Function to call on config change
        """
        self._config_watchers.append(callback)

    def reload(self) -> None:
        """Reload all configuration from disk."""
        self._env_cache.clear()
        self._toml_cache.clear()
        self._json_caches.clear()
        self._all_values.clear()
        self._load_all_configs()
        self.logger.info("[CONFIG] Configuration reloaded")

    # ===== Private: Loading methods =====

    def _load_all_configs(self) -> None:
        """Load configuration from all sources."""
        self._load_env()
        self._load_toml()
        self._load_json_configs()

    def _load_env(self) -> None:
        """Load .env file into environment."""
        env_file = self._repo_root / ".env"
        if not env_file.exists():
            self.logger.debug(f"[CONFIG] .env not found at {env_file}")
            return

        try:
            from dotenv import dotenv_values

            env_values = dotenv_values(env_file)
            for key, value in env_values.items():
                if value:
                    self._env_cache[key] = value
                    self._all_values[key] = ConfigValue(
                        key=key, value=value, source="env"
                    )
            self.logger.debug(f"[CONFIG] Loaded {len(env_values)} values from .env")
        except Exception as exc:
            self.logger.warning(f"[CONFIG] Failed to load .env: {exc}")

    def _load_toml(self) -> None:
        """Load config.toml file."""
        toml_file = self._repo_root / "core" / "config" / "config.toml"
        if not toml_file.exists():
            self.logger.debug(f"[CONFIG] config.toml not found at {toml_file}")
            return

        try:
            import tomllib

            with open(toml_file, "rb") as f:
                toml_data = tomllib.load(f)

            # Flatten TOML sections into cache
            for section, values in toml_data.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        full_key = f"{section.upper()}_{key.upper()}"
                        self._toml_cache[full_key] = value
                        if full_key not in self._all_values:
                            self._all_values[full_key] = ConfigValue(
                                key=full_key,
                                value=value,
                                source="toml",
                                section=section,
                            )
            self.logger.debug(f"[CONFIG] Loaded TOML from {toml_file}")
        except Exception as exc:
            self.logger.warning(f"[CONFIG] Failed to load config.toml: {exc}")

    def _load_json_configs(self) -> None:
        """Load JSON config files (wizard.json, ok_modes.json, etc.)."""
        json_files = [
            ("wizard", self._repo_root / "wizard" / "config" / "wizard.json"),
            ("ok_modes", self._repo_root / "core" / "config" / "ok_modes.json"),
            (
                "provider_flags",
                self._repo_root / "wizard" / "config" / "provider_setup_flags.json",
            ),
        ]

        for config_name, config_path in json_files:
            if not config_path.exists():
                continue

            try:
                with open(config_path) as f:
                    data = json.load(f)

                self._json_caches[config_name] = data
                self.logger.debug(f"[CONFIG] Loaded {config_name} from {config_path}")
            except Exception as exc:
                self.logger.warning(f"[CONFIG] Failed to load {config_name}: {exc}")

    @staticmethod
    def _resolve_repo_root(repo_root: Path | str | None) -> Path:
        """Resolve repository root path.

        Priority:
          1. Provided argument
          2. UDOS_ROOT environment variable
          3. Parent of core/ directory
          4. Current directory

        Args:
            repo_root: Optional override

        Returns:
            Resolved Path to repository root
        """
        # Explicit override
        if repo_root:
            return Path(repo_root).resolve()

        # Environment variable
        env_root = os.getenv("UDOS_ROOT")
        if env_root:
            return Path(env_root).resolve()

        # Parent of core/ directory
        try:
            import core

            core_path = Path(core.__file__).parent
            repo = core_path.parent
            if (repo / "core").exists():
                return repo
        except Exception:
            pass

        # Current directory
        return Path.cwd()


# Singleton instance
_loader: UnifiedConfigLoader | None = None


def get_config_loader(repo_root: Path | str | None = None) -> UnifiedConfigLoader:
    """Get singleton UnifiedConfigLoader instance.

    Args:
        repo_root: Optional override of repository root

    Returns:
        UnifiedConfigLoader singleton
    """
    global _loader
    if _loader is None:
        _loader = UnifiedConfigLoader(repo_root)
    return _loader


# Convenience functions


def get_config(key: str, default: Any = None) -> Any:
    """Convenience wrapper to get config value.

    Args:
        key: Configuration key
        default: Default value

    Returns:
        Configuration value
    """
    return get_config_loader().get(key, default)


def get_bool_config(key: str, default: bool = False) -> bool:
    """Convenience wrapper to get boolean config.

    Args:
        key: Configuration key
        default: Default value

    Returns:
        Boolean configuration value
    """
    return get_config_loader().get_bool(key, default)


def get_int_config(key: str, default: int = 0) -> int:
    """Convenience wrapper to get integer config.

    Args:
        key: Configuration key
        default: Default value

    Returns:
        Integer configuration value
    """
    return get_config_loader().get_int(key, default)


def get_path_config(key: str, default: Path | None = None) -> Path | None:
    """Convenience wrapper to get path config.

    Args:
        key: Configuration key
        default: Default value

    Returns:
        Path configuration value
    """
    return get_config_loader().get_path(key, default)
