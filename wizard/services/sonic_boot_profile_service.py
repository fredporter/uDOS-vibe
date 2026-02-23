"""Sonic boot profile and reboot routing service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.json_utils import read_json_file, write_json_file
from core.services.time_utils import utc_now_iso_z

class SonicBootProfileService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.sonic_root = self.repo_root / "sonic"
        self.boot_selector_path = self.sonic_root / "config" / "boot-selector.json"
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "boot-route.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_boot_selector(self) -> Dict[str, Any]:
        return read_json_file(self.boot_selector_path, default={"targets": []})

    def list_profiles(self) -> Dict[str, Any]:
        payload = self._load_boot_selector()
        targets: List[Dict[str, Any]] = payload.get("targets") or []
        return {
            "name": payload.get("name", "Sonic Boot Selector"),
            "version": payload.get("version"),
            "profiles": targets,
            "count": len(targets),
            "source": str(self.boot_selector_path),
        }

    def _read_route_state(self) -> Optional[Dict[str, Any]]:
        return read_json_file(self.state_path, default=None)

    def get_route_status(self) -> Dict[str, Any]:
        active = self._read_route_state()
        return {
            "active_route": active,
            "state_path": str(self.state_path),
        }

    def set_reboot_route(self, profile_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        profiles = self.list_profiles().get("profiles") or []
        selected = next((item for item in profiles if item.get("id") == profile_id), None)
        if not selected:
            raise KeyError(f"Unknown boot profile: {profile_id}")

        payload = {
            "profile_id": profile_id,
            "profile_name": selected.get("name"),
            "type": selected.get("type"),
            "distribution": selected.get("distribution"),
            "tier": selected.get("tier"),
            "reason": reason or "manual route selection",
            "routed_at": utc_now_iso_z(),
            "reboot_command": "sudo reboot",
        }
        write_json_file(self.state_path, payload, indent=2)
        return payload


def get_sonic_boot_profile_service(repo_root: Optional[Path] = None) -> SonicBootProfileService:
    return SonicBootProfileService(repo_root=repo_root)
