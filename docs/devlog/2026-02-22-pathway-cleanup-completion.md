# Pathway Cleanup Completion

Date: 2026-02-22

## Summary

Completed the roadmap pathway-cleanup item by removing dead legacy runtime code and locking remaining legacy entrypoints as explicit compatibility wrappers.

## Changes

- Removed dead TUI legacy entrypoint:
  - Deleted `core/tui/ucode_legacy_main.py`
- Strengthened wrapper contract checks:
  - Updated `wizard/tests/legacy_entrypoint_wrapper_test.py`
  - Added checks that:
    - API legacy entrypoint maps to modular runtime (`distribution/plugins/api/server.py` -> `server_modular`)
    - Sonic legacy service maps to plugin runtime (`wizard/services/sonic_service.py` -> `sonic_plugin_service`)
    - Removed TUI legacy module stays absent (`core/tui/ucode_legacy_main.py`)
- Updated roadmap status:
  - `docs/roadmap.md` marks pathway cleanup complete with explicit retained/active surface note for `wizard/web/app.py`.

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
  wizard/tests/legacy_entrypoint_wrapper_test.py \
  core/tests/logging_contract_phase2_test.py \
  core/tests/test_logging_api_v1_3.py \
  core/tests/path_service_test.py \
  core/tests/packaging_manifest_service_test.py \
  wizard/tests/path_utils_scheme_test.py \
  wizard/tests/workspace_routes_test.py \
  wizard/tests/sonic_build_service_artifacts_test.py \
  wizard/tests/sonic_linux_launcher_service_test.py \
  wizard/tests/sonic_platform_linux_launcher_test.py -q
```

Result: `32 passed`.
