# I7: RC1 Validation Sweep and Roadmap Checkpoint

Date: 2026-02-23
Status: Completed

## Scope

Close RC1 readiness validation by running the profile matrix with plugin autoload disabled, fixing surfaced regressions, and updating roadmap checkpoint status.

## Commands Run

```bash
# Core profile
uv sync --group dev --extra udos
./scripts/run_pytest_profile.sh core

# Wizard profile
uv sync --group dev --extra udos-wizard
./scripts/run_pytest_profile.sh wizard

# Full profile
uv sync --group dev --extra udos-full
./scripts/run_pytest_profile.sh full

# Targeted validation (explicit plugin list)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  wizard/tests/sonic_platform_gui_entrypoints_test.py

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  core/tests/logging_contract_phase2_test.py \
  tests/core/test_file_logging.py
```

## Final Matrix Results

- Core profile: `1753 passed, 3 skipped`.
- Wizard profile: `2008 passed, 3 skipped`.
- Full profile: `2008 passed, 3 skipped`.

## Issues Found During I7 and Fixes

1. Sonic GUI rebuild action default-force regression
- Symptom: `wizard/tests/sonic_platform_gui_entrypoints_test.py` expected rebuild action to default to `force=True` when payload omitted `force`.
- Fix: `wizard/routes/platform_routes.py` now interprets omitted `force` via `payload.model_fields_set` and defaults rebuild to `True` while still honoring explicit `false`.

2. Logging test flake after `vibe.core.utils` module reload/delete
- Symptom: profile runs intermittently failed in `tests/core/test_file_logging.py` because patching `vibe.core.utils.LOG_DIR/LOG_FILE` could target a live module while tests invoked a stale imported `apply_logging_config` function after module cache manipulation.
- Fix: `vibe/core/utils.py` now resolves `LOG_DIR/LOG_FILE` from live `sys.modules["vibe.core.utils"]` on each call, then derives file path deterministically from live `LOG_DIR`.

3. Profile-environment mismatch during matrix execution
- Symptom: running wizard profile after core sync caused `ModuleNotFoundError: fastapi`.
- Resolution: run each lane with matching `uv sync --extra` before its profile script.

## Remaining Risk

- No blocking failures remain in RC1 matrix lanes.
- Prior flaky logging behavior was resolved with live-module lookup and targeted regression validation.

## Roadmap Checkpoint

- RC1 matrix criterion is now complete.
- I7 is complete.
- Roadmap advanced to activate `v1.5-GA Hardening` queue.
