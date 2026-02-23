# App Externalization Cleanup (Startup + Tests)

Date: 2026-02-23

## Summary

Aligned repo runtime boundaries with the app externalization decision: removed in-repo `wizard.web.app` coupling and updated startup/test surfaces to target Wizard server runtime only.

## Changes

- Removed embedded app module:
  - Deleted `wizard/web/app.py`
- Updated startup script:
  - `wizard/web/start_wizard_web.sh`
  - Now runs only: `uv run wizard/server.py --no-interactive`
  - No `wizard.web.app` import/start path remains
- Updated web README to externalized-app status:
  - `wizard/web/README.md`
- Removed app-coupled tests and added runtime-boundary tests:
  - Deleted `wizard/tests/test_config_page.py`
  - Added `wizard/tests/startup_script_contract_test.py`
  - Updated `core/tests/ucode_runtime_boundary_test.py`
- Updated packaging snapshot list:
  - Removed stale `wizard/web/app.py` entry from `distribution/test-packages/udos-wizard.tcz.list`

## Validation

Executed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  wizard/tests/startup_script_contract_test.py \
  core/tests/ucode_runtime_boundary_test.py \
  wizard/tests/legacy_entrypoint_wrapper_test.py \
  core/tests/logging_contract_phase2_test.py \
  core/tests/test_logging_api_v1_3.py -q
```

## Notes

- This cleanup intentionally removes backward-compat startup behavior for embedded app runtime.
- Canonical local startup now means Wizard server runtime only.
