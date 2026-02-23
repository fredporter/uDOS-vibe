"""
uHOME Standalone Install — Hardware Preflight Checker
=======================================================

Validates target hardware against the uHOME OS minimum and recommended
profiles before Sonic begins a standalone uHOME deployment.

Hardware probe dict keys (all optional — missing keys are treated as unknown):
    cpu_cores       int   — logical CPU core count
    ram_gb          float — total RAM in GB
    storage_gb      float — primary OS storage in GB
    media_storage_gb float — dedicated media/recording storage in GB
    has_gigabit     bool  — Gigabit Ethernet present
    tuner_count     int   — number of detected HDHomeRun tuners on LAN
    has_hdmi        bool  — HDMI output present
    has_bluetooth   bool  — Bluetooth adapter present
    has_usb_ports   int   — number of USB-A ports
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Hardware profiles (from uHOME-spec.md)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UHOMEHardwareProfile:
    """Minimum and recommended hardware thresholds for uHOME deployments."""

    # Minimum
    min_cpu_cores: int = 4
    min_ram_gb: float = 8.0
    min_storage_gb: float = 256.0
    min_media_storage_gb: float = 2000.0  # 2 TB
    min_tuner_count: int = 1

    # Recommended
    rec_cpu_cores: int = 6
    rec_ram_gb: float = 16.0
    rec_storage_gb: float = 512.0
    rec_media_storage_gb: float = 4000.0  # 4 TB
    rec_tuner_count: int = 2

    # Mandatory peripherals
    require_hdmi: bool = True
    require_gigabit: bool = True
    min_usb_ports: int = 2


DEFAULT_PROFILE = UHOMEHardwareProfile()


# ---------------------------------------------------------------------------
# Preflight result
# ---------------------------------------------------------------------------

@dataclass
class UHOMEPreflightResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    probe: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "probe": self.probe,
        }


# ---------------------------------------------------------------------------
# Preflight logic
# ---------------------------------------------------------------------------

def preflight_check(
    probe: dict[str, Any],
    profile: UHOMEHardwareProfile = DEFAULT_PROFILE,
) -> UHOMEPreflightResult:
    """
    Validate a hardware probe dict against the given uHOME hardware profile.

    Returns a UHOMEPreflightResult with pass/fail status, blocking issues,
    and non-blocking warnings.
    """
    issues: list[str] = []
    warnings: list[str] = []

    cpu = probe.get("cpu_cores")
    if cpu is not None:
        if cpu < profile.min_cpu_cores:
            issues.append(
                f"CPU: {cpu} cores < minimum {profile.min_cpu_cores} — uHOME DVR "
                "requires at least a quad-core processor."
            )
        elif cpu < profile.rec_cpu_cores:
            warnings.append(
                f"CPU: {cpu} cores meets minimum but {profile.rec_cpu_cores}+ recommended "
                "for smooth background Comskip processing."
            )

    ram = probe.get("ram_gb")
    if ram is not None:
        if ram < profile.min_ram_gb:
            issues.append(
                f"RAM: {ram:.1f} GB < minimum {profile.min_ram_gb:.0f} GB — "
                "insufficient for concurrent recording + Jellyfin playback."
            )
        elif ram < profile.rec_ram_gb:
            warnings.append(
                f"RAM: {ram:.1f} GB meets minimum but {profile.rec_ram_gb:.0f} GB recommended."
            )

    storage = probe.get("storage_gb")
    if storage is not None and storage < profile.min_storage_gb:
        issues.append(
            f"OS storage: {storage:.0f} GB < minimum {profile.min_storage_gb:.0f} GB."
        )

    media = probe.get("media_storage_gb")
    if media is not None:
        if media < profile.min_media_storage_gb:
            issues.append(
                f"Media storage: {media:.0f} GB < minimum {profile.min_media_storage_gb:.0f} GB — "
                "uHOME DVR requires at least 2 TB for recordings."
            )
        elif media < profile.rec_media_storage_gb:
            warnings.append(
                f"Media storage: {media:.0f} GB — {profile.rec_media_storage_gb:.0f} GB recommended "
                "for a growing broadcast movie archive."
            )

    gigabit = probe.get("has_gigabit")
    if gigabit is not None and profile.require_gigabit and not gigabit:
        issues.append(
            "Network: Gigabit Ethernet required for reliable HDHomeRun stream + LAN playback."
        )

    hdmi = probe.get("has_hdmi")
    if hdmi is not None and profile.require_hdmi and not hdmi:
        issues.append(
            "Display: HDMI output required for uHOME console mode (direct TV connection)."
        )

    tuners = probe.get("tuner_count")
    if tuners is not None:
        if tuners < profile.min_tuner_count:
            issues.append(
                f"Tuner: {tuners} HDHomeRun tuner(s) found — at least {profile.min_tuner_count} required."
            )
        elif tuners < profile.rec_tuner_count:
            warnings.append(
                f"Tuner: {tuners} tuner — {profile.rec_tuner_count}+ recommended to record "
                "while watching time-shifted content."
            )

    usb = probe.get("has_usb_ports")
    if usb is not None and usb < profile.min_usb_ports:
        warnings.append(
            f"USB: {usb} port(s) — {profile.min_usb_ports}+ recommended for controller + peripherals."
        )

    bluetooth = probe.get("has_bluetooth")
    if bluetooth is not None and not bluetooth:
        warnings.append(
            "Bluetooth: not detected — Bluetooth 5.0 recommended for wireless game controller support."
        )

    return UHOMEPreflightResult(
        passed=len(issues) == 0,
        issues=issues,
        warnings=warnings,
        probe=probe,
    )
