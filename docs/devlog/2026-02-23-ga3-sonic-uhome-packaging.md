# GA3: Sonic Screwdriver Standalone uHOME Packaging

Date: 2026-02-23
Status: Completed

## Scope

Implement the Sonic Screwdriver artifact contract and install plan builder
required by the `Pre-v1.5 Stable: Sonic Screwdriver standalone uHOME
packaging/installer lane` milestone.

## What Changed

### New: `sonic/core/uhome_preflight.py`

Hardware compatibility checker for standalone uHOME deployments.

- `UHOMEHardwareProfile` — frozen dataclass encoding minimum and recommended
  hardware thresholds (derived from `uHOME-spec.md`):
  - Minimum: 4 CPU cores, 8 GB RAM, 256 GB OS storage, 2 TB media storage,
    1 tuner, Gigabit Ethernet, HDMI, 2 USB ports.
  - Recommended: 6 CPU cores, 16 GB RAM, 512 GB OS storage, 4 TB media, 2 tuners.
- `UHOMEPreflightResult` — result dataclass with `passed`, `issues` (blocking),
  `warnings` (non-blocking), and the original `probe` dict.
- `preflight_check(probe, profile)` — validates a hardware probe dict and
  returns blocking issues + non-blocking warnings. Missing probe keys are
  treated as unknown and skipped (no false positives).

### New: `sonic/core/uhome_bundle.py`

Artifact contract for uHOME install bundles produced by Sonic.

- `UHOMEBundleComponent` — single installable component with version pinning,
  relative artifact path, SHA-256 checksum, install target, and optional flag.
- `UHOMEBundleManifest` — top-level bundle manifest serialized to
  `uhome-bundle.json`. Records bundle_id, uhome_version, sonic_version,
  schema_version, created_at, and the component list.
- `UHOMERollbackRecord` — pre-install state snapshot (snapshot_paths,
  pre_install_hashes, rollback_token) serialized to `rollback/rollback.json`.
- `compute_checksum(path)` — SHA-256 of a file (64 KB chunks).
- `verify_checksum(path, expected)` — checksum verification (returns bool).
- `write_bundle_manifest / read_bundle_manifest` — JSON I/O for the manifest.
- `write_rollback_record / read_rollback_record` — JSON I/O for rollback state.
- `verify_bundle(manifest, bundle_dir)` — verifies all component artifacts
  exist and have correct checksums; optional components produce warnings, not
  errors.
- `BundleVerifyResult` — result dataclass with `valid`, `missing`, `corrupt`,
  `warnings`.

### New: `sonic/core/uhome_installer.py`

Standalone install plan builder (plan-only; no disk writes).

- `UHOMEInstallOptions` — tunable install parameters: `install_root`,
  `enable_autologin_kiosk`, `kiosk_user`, `enable_ha_bridge`, `dry_run`.
- `InstallPhase` (enum) — PREFLIGHT, VERIFY, STAGE, CONFIGURE, ENABLE,
  FINALIZE.
- `UHOMEInstallStep` — one ordered action with phase, action name,
  description, params dict, and blocking flag.
- `UHOMEInstallPlan` — complete ordered step list; `ready=True` only when
  both preflight and bundle verification pass.
- `build_uhome_install_plan(bundle_dir, probe, opts, profile, rollback)`:
  - Phase 1 PREFLIGHT: hardware check; aborts plan if failed.
  - Phase 2 VERIFY: reads bundle manifest + verifies checksums; aborts if
    manifest absent or any required component missing/corrupt.
  - Phase 3 STAGE: one step per component (source → install_target).
  - Phase 4 CONFIGURE: uhome_config, jellyfin_config, comskip_config; optional
    ha_bridge_config if `enable_ha_bridge=True`.
  - Phase 5 ENABLE: jellyfin.service, uhome-dvr.service; optional
    uhome-kiosk.service autologin for boot-to-controller UX.
  - Phase 6 FINALIZE: install receipt + optional rollback token commit.

Post-install UX target: `enable_autologin_kiosk=True` (default) configures
systemd autologin + `uhome-kiosk.service` so the system boots directly into
the game-controller-friendly Jellyfin/DVR frontend with no desktop session.

## Tests Run

```
core/tests/sonic_uhome_bundle_test.py  21 passed in 1.13s
```

Test coverage:

**Checksum utilities (4 tests)**
- `test_compute_checksum` — SHA-256 matches known digest.
- `test_verify_checksum_passes` — correct hash returns True.
- `test_verify_checksum_fails_on_wrong_hash` — wrong hash returns False.
- `test_verify_checksum_missing_file` — missing file returns False.

**Manifest I/O round-trip (3 tests)**
- `test_write_and_read_bundle_manifest` — serializes and deserializes correctly.
- `test_read_bundle_manifest_missing_returns_none` — absent file → None.
- `test_read_bundle_manifest_malformed_returns_none` — bad JSON → None.

**Rollback record I/O (2 tests)**
- `test_write_and_read_rollback_record` — round-trips token + paths + hashes.
- `test_read_rollback_record_missing_returns_none` — absent file → None.

**Bundle verification (4 tests)**
- `test_verify_bundle_all_pass` — valid bundle → `valid=True`, no issues.
- `test_verify_bundle_missing_artifact` — required artifact absent → `valid=False`, component in `missing`.
- `test_verify_bundle_corrupt_checksum` — wrong checksum → `valid=False`, component in `corrupt`.
- `test_verify_bundle_optional_missing_is_warning` — optional artifact absent → `valid=True`, warning emitted.

**Install plan builder (8 tests)**
- `test_plan_ready_on_passing_probe_and_valid_bundle` — all 6 phases present, `ready=True`.
- `test_plan_includes_kiosk_step_by_default` — autologin kiosk step in ENABLE phase.
- `test_plan_no_kiosk_when_disabled` — `enable_autologin_kiosk=False` omits kiosk step.
- `test_plan_not_ready_when_preflight_fails` — failing probe → `ready=False`, STAGE/CONFIGURE absent.
- `test_plan_idempotent` — identical inputs → identical step count and phase/action sequence.
- `test_plan_includes_rollback_commit_step` — rollback record → FINALIZE includes `commit_rollback_token`.
- `test_plan_no_rollback_step_without_record` — no rollback → `commit_rollback_token` absent.
- `test_plan_to_dict_is_json_serializable` — `plan.to_dict()` roundtrips to valid JSON.

## Remaining Risk

- `uhome_installer.py` produces a plan but does not execute it; a Sonic
  executor wiring the plan to real disk operations is GA4/post-GA3 scope.
- Kiosk service (`uhome-kiosk.service`) is referenced by name; the systemd
  unit file template is not yet in the repository.
- `ha_bridge_enabled` wiring in the install plan generates a configure step
  only; actual Wizard config mutation is handled by the HA bridge service
  (GA2 scope, complete).

## Exit Condition

GA3 complete. Roadmap advanced; GA4 (Wizard networking/beacon stabilization)
is next.
