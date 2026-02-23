"""Windows packaging adapter executor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.services.packaging_adapters.manifest_reader import read_platform


def entertainment_config(repo_root: Path) -> dict[str, Any]:
    windows = read_platform(repo_root, "windows")
    media_steps = dict(windows.get("media_game_image_steps") or {})
    shell_defaults = dict(windows.get("shell_defaults") or {})
    return {
        "scripts_root": media_steps.get("scripts_root"),
        "mode_switch_script": media_steps.get("mode_switch_script"),
        "offline_root": media_steps.get("offline_root"),
        "mode_switch": {
            "media_identifier": media_steps.get("media_identifier"),
            "game_identifier": media_steps.get("game_identifier"),
            "media_partition": media_steps.get("media_partition"),
            "game_partition": media_steps.get("game_partition"),
            "boot_timeout_seconds": media_steps.get("boot_timeout_seconds"),
        },
        "shell_paths": {
            "kodi": shell_defaults.get("kodi"),
            "playnite": shell_defaults.get("playnite"),
            "steam": shell_defaults.get("steam"),
            "custom": shell_defaults.get("custom"),
        },
        "default_game_launcher_path": shell_defaults.get("default_game_launcher_path"),
    }


def shell_path(repo_root: Path, mode: str) -> str:
    config = entertainment_config(repo_root)
    paths = config.get("shell_paths") or {}
    value = str(paths.get(mode) or "").strip()
    if value:
        return value
    raise ValueError(f"windows.shell_defaults.{mode} is required")
