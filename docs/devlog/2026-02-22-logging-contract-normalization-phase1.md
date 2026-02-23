# Logging Contract Normalization Phase 1

Date: 2026-02-22

## Summary

Completed phase-1 logging contract normalization by removing duplicate logger compatibility logic between core and wizard wrappers and centralizing argument normalization in `core/services/logging_api.py`.

## Changes

- Updated `core/services/logging_api.py`:
  - `get_logger()` now accepts `default_component` (default: `core`) to centralize backward-compatibility behavior for `get_logger("category")` usage.
- Updated `wizard/services/logging_api.py`:
  - Removed duplicate known-component fallback logic.
  - Delegates logger normalization to core via `default_component="wizard"`.
  - Removed inline suppression import style and switched to direct imports.
- Added/updated tests:
  - `core/tests/test_logging_api_v1_3.py`
    - Added backward-compatibility assertion for core default component/category mapping.
  - `wizard/tests/logging_api_wrapper_test.py`
    - Added wizard-wrapper assertion for wizard default component/category mapping.

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
  core/tests/test_logging_api_v1_3.py \
  wizard/tests/logging_api_wrapper_test.py \
  core/tests/path_service_test.py \
  core/tests/packaging_manifest_service_test.py \
  wizard/tests/path_utils_scheme_test.py \
  wizard/tests/workspace_routes_test.py \
  wizard/tests/sonic_build_service_artifacts_test.py \
  wizard/tests/sonic_linux_launcher_service_test.py \
  wizard/tests/sonic_platform_linux_launcher_test.py -q
```

Result: `26 passed`.

## Remaining Work

- Migrate non-core logging stacks to the same sink/contract:
  - `distribution/plugins/api/server_modular.py` (`logging.basicConfig` + rotating handlers)
  - `vibe/core/utils.py` (rotating handler stack)
- Enforce single sink policy for runtime logs under `memory/logs/udos` with export adapters where needed.
