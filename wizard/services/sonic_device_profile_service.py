"""Sonic device profile auto-detection and recommendations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.sonic_profile_matrix import (
    SonicTier,
    detect_hardware_context,
    get_tier_recommendations,
    resolve_gpu_lane,
    resolve_tier,
)


class SonicDeviceProfileService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent

    def auto_detect_profile(self) -> Dict[str, Any]:
        ctx = detect_hardware_context()
        tier = resolve_tier(ram_gb=ctx.ram_gb, cpu_count=ctx.cpu_count)
        gpu_lane = resolve_gpu_lane(arch=ctx.arch, processor=ctx.processor, headless=ctx.headless)

        return {
            "detected": {
                "hostname": ctx.hostname,
                "system": ctx.system,
                "arch": ctx.arch,
                "processor": ctx.processor,
                "cpu_count": ctx.cpu_count,
                "ram_gb": ctx.ram_gb,
                "uefi_native": ctx.uefi_native,
                "headless": ctx.headless,
                "gpu_lane": gpu_lane.value,
            },
            "tier": tier.value,
        }

    def get_recommendations(self) -> Dict[str, Any]:
        profile = self.auto_detect_profile()
        tier = SonicTier(profile["tier"])
        detected = profile["detected"]
        recommendations = get_tier_recommendations(tier)

        return {
            "profile": profile,
            "recommendations": {
                "boot_profile_id": recommendations["boot_profile_id"],
                "windows_mode": recommendations["windows_mode"],
                "windows_launcher": recommendations["windows_launcher"],
                "wizard_profile": recommendations["wizard_profile"],
                "notes": [
                    "Auto-detected recommendations are advisory and should be confirmed before flashing.",
                    "Use Sonic boot route + Windows launcher mode endpoints to apply these values.",
                ],
            },
            "confidence": 0.55 if detected["ram_gb"] is None else 0.7,
        }


def get_sonic_device_profile_service(repo_root: Optional[Path] = None) -> SonicDeviceProfileService:
    return SonicDeviceProfileService(repo_root=repo_root)
