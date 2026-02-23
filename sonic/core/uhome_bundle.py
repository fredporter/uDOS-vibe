"""
uHOME Standalone Bundle — Artifact Contract
============================================

Defines the artifact contract for uHOME install bundles produced by Sonic.

A uHOME bundle is a self-contained directory that Sonic stages on the target
device.  The bundle manifest records:

- Which uHOME components are included and at which versions (version pinning).
- SHA-256 checksums for every component artifact (tamper/corruption detection).
- A rollback token and pre-install snapshot record so a failed install can
  restore the previous state.

Bundle directory layout (written by uhome_installer, verified here):

    <bundle_dir>/
        uhome-bundle.json       ← manifest (this module's schema)
        components/
            jellyfin/           ← media server
            comskip/            ← ad-detection binary
            hdhomerun_config/   ← HDHomeRun config tool
            udos_uhome/         ← uDOS uHOME integration layer
        rollback/
            rollback.json       ← pre-install snapshot record (if any)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

BUNDLE_MANIFEST_FILENAME = "uhome-bundle.json"
ROLLBACK_FILENAME = "rollback.json"
BUNDLE_SCHEMA_VERSION = "1.0"

# Canonical component IDs in a uHOME bundle.
UHOME_COMPONENT_IDS = [
    "jellyfin",
    "comskip",
    "hdhomerun_config",
    "udos_uhome",
]


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class UHOMEBundleComponent:
    """A single installable component within a uHOME bundle."""

    component_id: str          # e.g. "jellyfin"
    display_name: str          # e.g. "Jellyfin Media Server"
    version: str               # pinned version string, e.g. "10.8.13"
    artifact_path: str         # relative path inside bundle_dir
    sha256: str                # hex-encoded SHA-256 checksum of the artifact
    install_target: str        # absolute install path on the target system
    optional: bool = False     # if True, missing artifact is a warning not an error


@dataclass
class UHOMERollbackRecord:
    """Pre-install state snapshot used to restore the system on rollback."""

    rollback_token: str             # opaque token tying this record to a manifest
    snapshot_paths: list[str] = field(default_factory=list)   # backed-up paths
    pre_install_hashes: dict[str, str] = field(default_factory=dict)  # path → sha256
    notes: str = ""                 # human-readable rollback context

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UHOMERollbackRecord:
        return cls(
            rollback_token=data["rollback_token"],
            snapshot_paths=data.get("snapshot_paths", []),
            pre_install_hashes=data.get("pre_install_hashes", {}),
            notes=data.get("notes", ""),
        )


@dataclass
class UHOMEBundleManifest:
    """
    Top-level manifest for a uHOME install bundle.

    Written to ``uhome-bundle.json`` inside the bundle directory.
    """

    bundle_id: str                   # unique run identifier (e.g. ISO-8601 timestamp)
    uhome_version: str               # uHOME release version this bundle targets
    sonic_version: str               # Sonic version that produced this bundle
    schema_version: str              # bundle schema version (BUNDLE_SCHEMA_VERSION)
    created_at: str                  # ISO-8601 UTC timestamp
    components: list[UHOMEBundleComponent] = field(default_factory=list)
    rollback_token: str = ""         # links to UHOMERollbackRecord in rollback/
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UHOMEBundleManifest:
        components = [
            UHOMEBundleComponent(**c) for c in data.get("components", [])
        ]
        return cls(
            bundle_id=data["bundle_id"],
            uhome_version=data["uhome_version"],
            sonic_version=data["sonic_version"],
            schema_version=data.get("schema_version", BUNDLE_SCHEMA_VERSION),
            created_at=data["created_at"],
            components=components,
            rollback_token=data.get("rollback_token", ""),
            notes=data.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Checksum utilities
# ---------------------------------------------------------------------------

def compute_checksum(path: Path) -> str:
    """Return the hex-encoded SHA-256 digest of the file at *path*."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(path: Path, expected: str) -> bool:
    """Return True if *path* has SHA-256 *expected*, False otherwise."""
    if not path.exists():
        return False
    return compute_checksum(path) == expected


# ---------------------------------------------------------------------------
# Bundle I/O
# ---------------------------------------------------------------------------

def write_bundle_manifest(bundle_dir: Path, manifest: UHOMEBundleManifest) -> Path:
    """
    Serialize *manifest* to JSON inside *bundle_dir*.

    Returns the path of the written manifest file.
    """
    bundle_dir.mkdir(parents=True, exist_ok=True)
    out = bundle_dir / BUNDLE_MANIFEST_FILENAME
    out.write_text(json.dumps(manifest.to_dict(), indent=2))
    return out


def read_bundle_manifest(bundle_dir: Path) -> UHOMEBundleManifest | None:
    """
    Read and deserialize the bundle manifest from *bundle_dir*.

    Returns None if the manifest is absent or malformed.
    """
    path = bundle_dir / BUNDLE_MANIFEST_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return UHOMEBundleManifest.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def write_rollback_record(bundle_dir: Path, record: UHOMERollbackRecord) -> Path:
    """Serialize *record* into the bundle's rollback sub-directory."""
    rollback_dir = bundle_dir / "rollback"
    rollback_dir.mkdir(parents=True, exist_ok=True)
    out = rollback_dir / ROLLBACK_FILENAME
    out.write_text(json.dumps(record.to_dict(), indent=2))
    return out


def read_rollback_record(bundle_dir: Path) -> UHOMERollbackRecord | None:
    """
    Read and deserialize the rollback record from *bundle_dir/rollback/*.

    Returns None if absent or malformed.
    """
    path = bundle_dir / "rollback" / ROLLBACK_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return UHOMERollbackRecord.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Bundle verification
# ---------------------------------------------------------------------------

@dataclass
class BundleVerifyResult:
    valid: bool
    missing: list[str] = field(default_factory=list)    # component IDs with no artifact
    corrupt: list[str] = field(default_factory=list)    # component IDs with bad checksum
    warnings: list[str] = field(default_factory=list)   # non-fatal issues


def verify_bundle(manifest: UHOMEBundleManifest, bundle_dir: Path) -> BundleVerifyResult:
    """
    Verify all component artifacts in *bundle_dir* against the manifest.

    Checks:
    - Artifact file exists at the expected relative path.
    - SHA-256 checksum matches the pinned value in the manifest.
    - Optional components produce warnings (not errors) on missing artifact.
    """
    missing: list[str] = []
    corrupt: list[str] = []
    warnings: list[str] = []

    for comp in manifest.components:
        artifact = bundle_dir / comp.artifact_path
        if not artifact.exists():
            if comp.optional:
                warnings.append(
                    f"Optional component '{comp.component_id}' artifact not found: "
                    f"{comp.artifact_path}"
                )
            else:
                missing.append(comp.component_id)
            continue

        if comp.sha256 and not verify_checksum(artifact, comp.sha256):
            corrupt.append(comp.component_id)

    return BundleVerifyResult(
        valid=(len(missing) == 0 and len(corrupt) == 0),
        missing=missing,
        corrupt=corrupt,
        warnings=warnings,
    )
