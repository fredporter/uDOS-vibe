# M3.2 Packaging Script and Artifact Flow Validation

Date: 2026-02-22

## Goal

Validate packaging scripts and artifact-generation surfaces for release readiness.

## Work Completed

- Added packaging surface contract test:
  - `core/tests/packaging_surface_contract_test.py`
- Assertions cover:
  - Canonical packaging scripts exist:
    - `distribution/alpine-core/build-sonic-stick.sh`
    - `distribution/installer.sh`
    - `bin/install-udos-vibe.sh`
    - `tools/ci/validate_sonic_artifact_manifest.py`
  - `SonicBuildService` points to canonical build script path.

## Existing Flow Validation Used

- Ran Sonic artifact/release-readiness tests:
  - `wizard/tests/sonic_build_service_artifacts_test.py`
- Confirms manifest, checksum, and detached-signature readiness behavior.

## Notes

- `wizard/tests/publish_release_gates_test.py` remains gated by missing optional `fastapi` in core-only environment.
- Core/MCP workflow does not require FastAPI; Wizard profile adds it.

## Validation Commands

- `uv run pytest core/tests/packaging_surface_contract_test.py wizard/tests/sonic_build_service_artifacts_test.py -q`
- Result: 7 passed.
