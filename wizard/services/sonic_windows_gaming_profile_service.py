"""Sonic Windows gaming profile automation service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from core.services.json_utils import read_json_file, write_json_file
from core.services.time_utils import utc_now_iso_z
from wizard.services.sonic_profile_matrix import (
    detect_hardware_context,
    get_windows_profile_templates,
    resolve_gpu_lane,
)


class SonicWindowsGamingProfileService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "windows-gaming-profile.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._templates = self._build_templates()

    @staticmethod
    def _build_templates() -> dict[str, dict[str, Any]]:
        ctx = detect_hardware_context()
        lane = resolve_gpu_lane(arch=ctx.arch, processor=ctx.processor, headless=ctx.headless)
        return get_windows_profile_templates(lane)

    def _read_state(self) -> Dict[str, Any]:
        return read_json_file(
            self.state_path,
            default={"profile_id": None, "settings": {}, "updated_at": None},
        )

    def _write_state(self, payload: Dict[str, Any]) -> None:
        write_json_file(self.state_path, payload, indent=2)

    def list_profiles(self) -> Dict[str, Any]:
        return {
            "count": len(self._templates),
            "profiles": [{"id": key, "settings": value} for key, value in self._templates.items()],
            "active": self._read_state(),
            "state_path": str(self.state_path),
        }

    def apply_profile(self, profile_id: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        key = (profile_id or "").strip().lower()
        if key not in self._templates:
            raise ValueError(f"Unsupported gaming profile: {profile_id}")
        settings = dict(self._templates[key])
        if extra:
            settings.update(extra)
        payload = {
            "profile_id": key,
            "settings": settings,
            "updated_at": utc_now_iso_z(),
            "automation_status": "applied",
        }
        self._write_state(payload)
        return payload


def get_sonic_windows_gaming_profile_service(
    repo_root: Optional[Path] = None,
) -> SonicWindowsGamingProfileService:
    return SonicWindowsGamingProfileService(repo_root=repo_root)
