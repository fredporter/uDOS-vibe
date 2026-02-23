# 2026-02-23 Installer + Startup Entrypoint Cleanup

## Summary

Completed another cleanup pass to reduce duplicate startup/install pathways and enforce canonical routing behavior.

## Startup cleanup

- `wizard/web/start_wizard_web.sh` is now a thin wrapper over:
  - `bin/wizardd start`
- Removed duplicate direct launch logic from that script.
- Updated startup contract tests to lock this behavior.

## Installer cleanup

- Added cross-installer dispatch routing:
  - `bin/install-udos-vibe.sh` now routes TinyCore-style flags (`--tinycore`, `--tier`, `--packages`, `--from`, `--yes`, `--dry-run`) to `distribution/installer.sh`.
  - `distribution/installer.sh` now routes host-style flags (`--core`, `--wizard`, `--update`, `--skip-ollama`) to `bin/install-udos-vibe.sh`.
- Result: users can run either installer entrypoint and still land on the correct implementation path for intent.

## Validation

- Shell syntax checks:
  - `bash -n bin/install-udos-vibe.sh`
  - `sh -n distribution/installer.sh`
  - `bash -n wizard/web/start_wizard_web.sh`
- Test suites:
  - `wizard/tests/startup_script_contract_test.py`
  - `core/tests/ucode_runtime_boundary_test.py`
