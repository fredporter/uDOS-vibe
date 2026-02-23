"""
Tests for the uHOME bundle artifact contract and install plan builder.

Coverage:
- uhome_bundle: write/read manifest, checksum compute/verify, bundle verification
- uhome_installer: fresh install plan (ready), preflight-blocked plan, idempotent
  re-run (same bundle → same plan shape), rollback token propagation
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sonic.core.uhome_bundle import (
    BundleVerifyResult,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMERollbackRecord,
    BUNDLE_MANIFEST_FILENAME,
    BUNDLE_SCHEMA_VERSION,
    compute_checksum,
    read_bundle_manifest,
    read_rollback_record,
    verify_bundle,
    verify_checksum,
    write_bundle_manifest,
    write_rollback_record,
)
from sonic.core.uhome_installer import (
    InstallPhase,
    UHOMEInstallOptions,
    build_uhome_install_plan,
)
from sonic.core.uhome_preflight import UHOMEHardwareProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_artifact(bundle_dir: Path, rel_path: str, content: bytes = b"fake-payload") -> str:
    """Write a fake artifact file and return its SHA-256 hex digest."""
    artifact = bundle_dir / rel_path
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(content)
    h = hashlib.sha256(content).hexdigest()
    return h


def _minimal_component(bundle_dir: Path, component_id: str = "jellyfin") -> UHOMEBundleComponent:
    rel = f"components/{component_id}/payload.tar.gz"
    sha = _write_artifact(bundle_dir, rel)
    return UHOMEBundleComponent(
        component_id=component_id,
        display_name=component_id.capitalize(),
        version="1.0.0",
        artifact_path=rel,
        sha256=sha,
        install_target=f"/opt/uhome/{component_id}",
    )


def _minimal_manifest(bundle_dir: Path) -> UHOMEBundleManifest:
    comp = _minimal_component(bundle_dir)
    return UHOMEBundleManifest(
        bundle_id="test-bundle-001",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        components=[comp],
    )


def _passing_probe() -> dict:
    """Hardware probe dict that satisfies the DEFAULT_PROFILE minimums."""
    return {
        "cpu_cores": 6,
        "ram_gb": 16.0,
        "storage_gb": 512.0,
        "media_storage_gb": 4000.0,
        "has_gigabit": True,
        "has_hdmi": True,
        "tuner_count": 2,
        "has_usb_ports": 4,
        "has_bluetooth": True,
    }


def _failing_probe() -> dict:
    """Hardware probe dict that fails minimum CPU and RAM checks."""
    return {
        "cpu_cores": 2,
        "ram_gb": 4.0,
        "storage_gb": 128.0,
        "media_storage_gb": 500.0,
        "has_gigabit": False,
        "has_hdmi": False,
        "tuner_count": 0,
    }


# ---------------------------------------------------------------------------
# uhome_bundle: checksum utilities
# ---------------------------------------------------------------------------


def test_compute_checksum(tmp_path):
    f = tmp_path / "artifact.bin"
    content = b"hello uHOME"
    f.write_bytes(content)
    expected = hashlib.sha256(content).hexdigest()
    assert compute_checksum(f) == expected


def test_verify_checksum_passes(tmp_path):
    f = tmp_path / "artifact.bin"
    content = b"correct content"
    f.write_bytes(content)
    good_hash = hashlib.sha256(content).hexdigest()
    assert verify_checksum(f, good_hash) is True


def test_verify_checksum_fails_on_wrong_hash(tmp_path):
    f = tmp_path / "artifact.bin"
    f.write_bytes(b"content")
    assert verify_checksum(f, "deadbeef" * 8) is False


def test_verify_checksum_missing_file(tmp_path):
    assert verify_checksum(tmp_path / "nonexistent.bin", "abc") is False


# ---------------------------------------------------------------------------
# uhome_bundle: manifest I/O round-trip
# ---------------------------------------------------------------------------


def test_write_and_read_bundle_manifest(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    out = write_bundle_manifest(tmp_path, manifest)

    assert out.name == BUNDLE_MANIFEST_FILENAME
    assert out.exists()

    loaded = read_bundle_manifest(tmp_path)
    assert loaded is not None
    assert loaded.bundle_id == manifest.bundle_id
    assert loaded.uhome_version == manifest.uhome_version
    assert loaded.schema_version == BUNDLE_SCHEMA_VERSION
    assert len(loaded.components) == 1
    assert loaded.components[0].component_id == "jellyfin"


def test_read_bundle_manifest_missing_returns_none(tmp_path):
    assert read_bundle_manifest(tmp_path) is None


def test_read_bundle_manifest_malformed_returns_none(tmp_path):
    (tmp_path / BUNDLE_MANIFEST_FILENAME).write_text("{not valid json}")
    assert read_bundle_manifest(tmp_path) is None


# ---------------------------------------------------------------------------
# uhome_bundle: rollback record I/O
# ---------------------------------------------------------------------------


def test_write_and_read_rollback_record(tmp_path):
    record = UHOMERollbackRecord(
        rollback_token="tok-abc123",
        snapshot_paths=["/opt/uhome/jellyfin"],
        pre_install_hashes={"/opt/uhome/jellyfin/config.json": "aabbcc"},
        notes="Pre-GA3 install snapshot",
    )
    write_rollback_record(tmp_path, record)
    loaded = read_rollback_record(tmp_path)

    assert loaded is not None
    assert loaded.rollback_token == "tok-abc123"
    assert "/opt/uhome/jellyfin" in loaded.snapshot_paths
    assert loaded.pre_install_hashes["/opt/uhome/jellyfin/config.json"] == "aabbcc"


def test_read_rollback_record_missing_returns_none(tmp_path):
    assert read_rollback_record(tmp_path) is None


# ---------------------------------------------------------------------------
# uhome_bundle: bundle verification
# ---------------------------------------------------------------------------


def test_verify_bundle_all_pass(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    result = verify_bundle(manifest, tmp_path)
    assert result.valid is True
    assert result.missing == []
    assert result.corrupt == []


def test_verify_bundle_missing_artifact(tmp_path):
    comp = UHOMEBundleComponent(
        component_id="comskip",
        display_name="Comskip",
        version="0.81.0",
        artifact_path="components/comskip/comskip.tar.gz",
        sha256="abc123",
        install_target="/opt/uhome/comskip",
    )
    manifest = UHOMEBundleManifest(
        bundle_id="b2",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        components=[comp],
    )
    result = verify_bundle(manifest, tmp_path)
    assert result.valid is False
    assert "comskip" in result.missing


def test_verify_bundle_corrupt_checksum(tmp_path):
    rel = "components/jellyfin/payload.tar.gz"
    _write_artifact(tmp_path, rel, b"real content")
    comp = UHOMEBundleComponent(
        component_id="jellyfin",
        display_name="Jellyfin",
        version="10.8.13",
        artifact_path=rel,
        sha256="wronghash" * 4,  # intentionally wrong
        install_target="/opt/uhome/jellyfin",
    )
    manifest = UHOMEBundleManifest(
        bundle_id="b3",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        components=[comp],
    )
    result = verify_bundle(manifest, tmp_path)
    assert result.valid is False
    assert "jellyfin" in result.corrupt


def test_verify_bundle_optional_missing_is_warning(tmp_path):
    comp = UHOMEBundleComponent(
        component_id="hdhomerun_config",
        display_name="HDHomeRun Config",
        version="20230530",
        artifact_path="components/hdhomerun_config/hdhomerun_config",
        sha256="",
        install_target="/usr/local/bin/hdhomerun_config",
        optional=True,
    )
    manifest = UHOMEBundleManifest(
        bundle_id="b4",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        components=[comp],
    )
    result = verify_bundle(manifest, tmp_path)
    assert result.valid is True  # optional — not a hard failure
    assert result.missing == []
    assert len(result.warnings) == 1
    assert "optional" in result.warnings[0].lower()


# ---------------------------------------------------------------------------
# uhome_installer: build_uhome_install_plan — fresh install (ready)
# ---------------------------------------------------------------------------


def test_plan_ready_on_passing_probe_and_valid_bundle(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    plan = build_uhome_install_plan(tmp_path, _passing_probe())

    assert plan.ready is True
    assert plan.preflight_result.passed is True
    assert plan.verify_result is not None
    assert plan.verify_result.valid is True

    phases = {s.phase for s in plan.steps}
    assert InstallPhase.PREFLIGHT in phases
    assert InstallPhase.VERIFY in phases
    assert InstallPhase.STAGE in phases
    assert InstallPhase.CONFIGURE in phases
    assert InstallPhase.ENABLE in phases
    assert InstallPhase.FINALIZE in phases


def test_plan_includes_kiosk_step_by_default(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    plan = build_uhome_install_plan(tmp_path, _passing_probe())

    kiosk_actions = [s.action for s in plan.steps if s.phase == InstallPhase.ENABLE]
    assert "enable_kiosk_autologin" in kiosk_actions


def test_plan_no_kiosk_when_disabled(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    opts = UHOMEInstallOptions(enable_autologin_kiosk=False)
    plan = build_uhome_install_plan(tmp_path, _passing_probe(), opts=opts)

    kiosk_actions = [s.action for s in plan.steps if s.action == "enable_kiosk_autologin"]
    assert kiosk_actions == []


# ---------------------------------------------------------------------------
# uhome_installer: preflight-blocked plan
# ---------------------------------------------------------------------------


def test_plan_not_ready_when_preflight_fails(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    plan = build_uhome_install_plan(tmp_path, _failing_probe())

    assert plan.ready is False
    assert plan.preflight_result.passed is False
    assert len(plan.preflight_result.issues) > 0
    # verify + stage + configure steps should NOT be present
    assert plan.verify_result is None
    phases = {s.phase for s in plan.steps}
    assert InstallPhase.STAGE not in phases
    assert InstallPhase.CONFIGURE not in phases


# ---------------------------------------------------------------------------
# uhome_installer: idempotent re-run produces same shape
# ---------------------------------------------------------------------------


def test_plan_idempotent(tmp_path):
    """Calling build_uhome_install_plan twice with identical inputs yields the same plan shape."""
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    probe = _passing_probe()
    plan_a = build_uhome_install_plan(tmp_path, probe)
    plan_b = build_uhome_install_plan(tmp_path, probe)

    assert plan_a.ready == plan_b.ready
    assert len(plan_a.steps) == len(plan_b.steps)
    for a, b in zip(plan_a.steps, plan_b.steps):
        assert a.phase == b.phase
        assert a.action == b.action


# ---------------------------------------------------------------------------
# uhome_installer: rollback token propagation
# ---------------------------------------------------------------------------


def test_plan_includes_rollback_commit_step(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    rollback = UHOMERollbackRecord(
        rollback_token="tok-xyz",
        snapshot_paths=["/opt/uhome/jellyfin"],
    )
    plan = build_uhome_install_plan(tmp_path, _passing_probe(), rollback=rollback)

    finalize_actions = [s.action for s in plan.steps if s.phase == InstallPhase.FINALIZE]
    assert "commit_rollback_token" in finalize_actions

    commit_step = next(s for s in plan.steps if s.action == "commit_rollback_token")
    assert commit_step.params["rollback_token"] == "tok-xyz"


def test_plan_no_rollback_step_without_record(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    plan = build_uhome_install_plan(tmp_path, _passing_probe(), rollback=None)

    finalize_actions = [s.action for s in plan.steps if s.phase == InstallPhase.FINALIZE]
    assert "commit_rollback_token" not in finalize_actions


# ---------------------------------------------------------------------------
# uhome_installer: plan serialization
# ---------------------------------------------------------------------------


def test_plan_to_dict_is_json_serializable(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)

    plan = build_uhome_install_plan(tmp_path, _passing_probe())
    d = plan.to_dict()
    serialized = json.dumps(d)  # should not raise
    assert '"ready": true' in serialized
