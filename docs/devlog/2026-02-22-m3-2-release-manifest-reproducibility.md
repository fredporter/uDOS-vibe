# M3.2 Release Manifest/Signing/Checksum Reproducibility

Date: 2026-02-22

## Goal

Confirm release manifest/signing/checksum flow is consistent and reproducible.

## Work Completed

- Added reproducibility test:
  - `core/tests/release_manifest_reproducibility_test.py`
- Test creates a deterministic fixture build and verifies:
  - `get_release_readiness()` is release-ready for valid artifact/manifest/checksum/signature state.
  - repeated calls produce identical readiness outputs for checksums, signing, artifacts, and issues.

## Existing Coverage Reused

- `wizard/tests/sonic_build_service_artifacts_test.py`
  - readiness pass path
  - missing signatures path
  - pubkey-missing path
- `core/tests/packaging_surface_contract_test.py`
  - packaging script and service path contracts

## Validation

- `uv run pytest core/tests/release_manifest_reproducibility_test.py core/tests/packaging_surface_contract_test.py wizard/tests/sonic_build_service_artifacts_test.py -q`
- Result: 8 passed.

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.2` / "Confirm release manifest/signing/checksum flow is consistent and reproducible."
