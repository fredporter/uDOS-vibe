"""
uHOME Standalone Installer — Install Plan + Post-install UX
============================================================

Produces and validates the step-by-step install plan for a standalone uHOME
deployment.  This module does NOT execute destructive operations itself — it
emits an ``UHOMEInstallPlan`` that describes every action Sonic will take,
enabling dry-run inspection, test coverage, and human review before any disk
writes occur.

Post-install UX target:
    The system should boot directly into the uHOME controller UI (game-
    controller-friendly Jellyfin/DVR frontend) with no desktop session in
    between.  The install plan includes an autologin + kiosk-mode systemd
    unit step to achieve this.

Install phases:
    1. PREFLIGHT  — hardware compatibility check (uhome_preflight)
    2. VERIFY     — bundle artifact checksums (uhome_bundle)
    3. STAGE      — copy component artifacts to install targets
    4. CONFIGURE  — write uHOME service config files
    5. ENABLE     — enable systemd services + autologin kiosk unit
    6. FINALIZE   — record install receipt + rollback token

Usage:
    plan = build_uhome_install_plan(bundle_dir, probe, options)
    if plan.preflight_result.passed:
        # Hand plan to executor (not this module's responsibility)
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from sonic.core.uhome_bundle import (
    UHOMEBundleManifest,
    UHOMERollbackRecord,
    BundleVerifyResult,
    read_bundle_manifest,
    verify_bundle,
)
from sonic.core.uhome_preflight import (
    UHOMEHardwareProfile,
    UHOMEPreflightResult,
    DEFAULT_PROFILE,
    preflight_check,
)


# ---------------------------------------------------------------------------
# Install step model
# ---------------------------------------------------------------------------

class InstallPhase(str, Enum):
    PREFLIGHT = "preflight"
    VERIFY = "verify"
    STAGE = "stage"
    CONFIGURE = "configure"
    ENABLE = "enable"
    FINALIZE = "finalize"


@dataclass
class UHOMEInstallStep:
    phase: InstallPhase
    action: str          # short machine-readable action name
    description: str     # human-readable explanation
    params: dict[str, Any] = field(default_factory=dict)
    blocking: bool = True  # if True, failure aborts the install


# ---------------------------------------------------------------------------
# Install plan
# ---------------------------------------------------------------------------

@dataclass
class UHOMEInstallPlan:
    """
    Complete ordered list of steps for a standalone uHOME install.

    Produced by ``build_uhome_install_plan``; consumed by an executor
    (outside this module's scope).
    """

    bundle_dir: str
    dry_run: bool
    preflight_result: UHOMEPreflightResult
    verify_result: BundleVerifyResult | None  # None if preflight failed (skipped)
    steps: list[UHOMEInstallStep] = field(default_factory=list)
    ready: bool = False  # True only when preflight + verify both pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_dir": self.bundle_dir,
            "dry_run": self.dry_run,
            "ready": self.ready,
            "preflight": self.preflight_result.to_dict(),
            "verify": {
                "valid": self.verify_result.valid,
                "missing": self.verify_result.missing,
                "corrupt": self.verify_result.corrupt,
                "warnings": self.verify_result.warnings,
            } if self.verify_result else None,
            "steps": [
                {
                    "phase": s.phase.value,
                    "action": s.action,
                    "description": s.description,
                    "params": s.params,
                    "blocking": s.blocking,
                }
                for s in self.steps
            ],
        }


# ---------------------------------------------------------------------------
# Install options
# ---------------------------------------------------------------------------

@dataclass
class UHOMEInstallOptions:
    """Tunable options for the uHOME install plan generator."""

    install_root: str = "/opt/uhome"           # base install path on target
    enable_autologin_kiosk: bool = True        # boot-to-controller UX
    kiosk_user: str = "uhome"                  # local user for kiosk session
    enable_ha_bridge: bool = False             # opt-in: HA bridge (disabled default)
    dry_run: bool = False


# ---------------------------------------------------------------------------
# Step builders (private)
# ---------------------------------------------------------------------------

def _preflight_steps(result: UHOMEPreflightResult) -> list[UHOMEInstallStep]:
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.PREFLIGHT,
            action="hardware_preflight",
            description="Validate target hardware against uHOME minimum profile.",
            params={"passed": result.passed, "issues": result.issues, "warnings": result.warnings},
            blocking=True,
        )
    ]
    return steps


def _verify_steps(
    manifest: UHOMEBundleManifest,
    result: BundleVerifyResult,
) -> list[UHOMEInstallStep]:
    return [
        UHOMEInstallStep(
            phase=InstallPhase.VERIFY,
            action="verify_bundle_checksums",
            description=(
                f"Verify SHA-256 checksums for {len(manifest.components)} "
                "bundle component(s)."
            ),
            params={
                "valid": result.valid,
                "missing": result.missing,
                "corrupt": result.corrupt,
                "component_count": len(manifest.components),
            },
            blocking=True,
        )
    ]


def _stage_steps(
    manifest: UHOMEBundleManifest,
    bundle_dir: Path,
    install_root: str,
) -> list[UHOMEInstallStep]:
    steps = []
    for comp in manifest.components:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.STAGE,
                action="stage_component",
                description=f"Stage {comp.display_name} v{comp.version} → {comp.install_target}",
                params={
                    "component_id": comp.component_id,
                    "source": str(bundle_dir / comp.artifact_path),
                    "target": comp.install_target,
                    "sha256": comp.sha256,
                },
                blocking=not comp.optional,
            )
        )
    return steps


def _configure_steps(
    manifest: UHOMEBundleManifest,
    opts: UHOMEInstallOptions,
) -> list[UHOMEInstallStep]:
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_uhome_config",
            description="Write uHOME service configuration files.",
            params={
                "install_root": opts.install_root,
                "uhome_version": manifest.uhome_version,
                "ha_bridge_enabled": opts.enable_ha_bridge,
            },
        ),
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_jellyfin_config",
            description="Write Jellyfin media server initial configuration.",
            params={"install_root": opts.install_root},
        ),
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_comskip_config",
            description="Write Comskip ad-detection configuration (DVR integration).",
            params={"install_root": opts.install_root},
        ),
    ]
    if opts.enable_ha_bridge:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.CONFIGURE,
                action="write_ha_bridge_config",
                description="Write Home Assistant bridge configuration (ha_bridge_enabled=true).",
                params={"install_root": opts.install_root},
            )
        )
    return steps


def _enable_steps(opts: UHOMEInstallOptions) -> list[UHOMEInstallStep]:
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.ENABLE,
            action="enable_jellyfin_service",
            description="Enable and start jellyfin.service via systemd.",
            params={"service": "jellyfin"},
        ),
        UHOMEInstallStep(
            phase=InstallPhase.ENABLE,
            action="enable_uhome_dvr_service",
            description="Enable uhome-dvr.service for HDHomeRun recording integration.",
            params={"service": "uhome-dvr"},
        ),
    ]
    if opts.enable_autologin_kiosk:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.ENABLE,
                action="enable_kiosk_autologin",
                description=(
                    f"Configure systemd autologin for user '{opts.kiosk_user}' and "
                    "enable uhome-kiosk.service for boot-to-controller UX."
                ),
                params={
                    "kiosk_user": opts.kiosk_user,
                    "service": "uhome-kiosk",
                    "autologin_target": "multi-user.target",
                },
            )
        )
    return steps


def _finalize_steps(
    manifest: UHOMEBundleManifest,
    rollback: UHOMERollbackRecord | None,
) -> list[UHOMEInstallStep]:
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.FINALIZE,
            action="write_install_receipt",
            description="Record install receipt with bundle_id and component versions.",
            params={
                "bundle_id": manifest.bundle_id,
                "uhome_version": manifest.uhome_version,
                "sonic_version": manifest.sonic_version,
            },
        ),
    ]
    if rollback:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.FINALIZE,
                action="commit_rollback_token",
                description="Persist rollback token so a failed install can be reversed.",
                params={"rollback_token": rollback.rollback_token},
            )
        )
    return steps


# ---------------------------------------------------------------------------
# Public plan builder
# ---------------------------------------------------------------------------

def build_uhome_install_plan(
    bundle_dir: Path,
    probe: dict[str, Any],
    opts: UHOMEInstallOptions | None = None,
    profile: UHOMEHardwareProfile = DEFAULT_PROFILE,
    rollback: UHOMERollbackRecord | None = None,
) -> UHOMEInstallPlan:
    """
    Produce a complete ``UHOMEInstallPlan`` without executing anything.

    Args:
        bundle_dir: Path to the staged uHOME bundle directory.
        probe:      Hardware probe dict (see uhome_preflight for keys).
        opts:       Install options (defaults to ``UHOMEInstallOptions()``).
        profile:    Hardware profile thresholds (defaults to ``DEFAULT_PROFILE``).
        rollback:   Pre-install rollback record if a prior state was snapshotted.

    Returns:
        An ``UHOMEInstallPlan`` with ``ready=True`` iff preflight passes and
        the bundle verifies cleanly.
    """
    if opts is None:
        opts = UHOMEInstallOptions()

    steps: list[UHOMEInstallStep] = []

    # Phase 1: preflight
    preflight_result = preflight_check(probe, profile)
    steps.extend(_preflight_steps(preflight_result))

    if not preflight_result.passed:
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=None,
            steps=steps,
            ready=False,
        )

    # Phase 2: verify bundle
    manifest = read_bundle_manifest(bundle_dir)
    if manifest is None:
        # Synthesize a verify failure step
        verify_result = BundleVerifyResult(
            valid=False,
            missing=["<manifest>"],
            corrupt=[],
            warnings=["uhome-bundle.json not found in bundle directory."],
        )
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.VERIFY,
                action="verify_bundle_checksums",
                description="Bundle manifest not found — cannot proceed.",
                params={"valid": False},
                blocking=True,
            )
        )
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=verify_result,
            steps=steps,
            ready=False,
        )

    verify_result = verify_bundle(manifest, bundle_dir)
    steps.extend(_verify_steps(manifest, verify_result))

    if not verify_result.valid:
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=verify_result,
            steps=steps,
            ready=False,
        )

    # Phases 3-6: stage → configure → enable → finalize
    steps.extend(_stage_steps(manifest, bundle_dir, opts.install_root))
    steps.extend(_configure_steps(manifest, opts))
    steps.extend(_enable_steps(opts))
    steps.extend(_finalize_steps(manifest, rollback))

    return UHOMEInstallPlan(
        bundle_dir=str(bundle_dir),
        dry_run=opts.dry_run,
        preflight_result=preflight_result,
        verify_result=verify_result,
        steps=steps,
        ready=True,
    )
