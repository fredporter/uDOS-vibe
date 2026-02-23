# Logging Contract Normalization Phase 2

Date: 2026-02-22

## Summary

Completed phase-2 logging contract migration by moving the remaining non-core rotating/basicConfig stacks to the core logging API sink path and adding coverage for contract behavior.

## Changes

- Migrated API modular server logging:
  - `distribution/plugins/api/server_modular.py`
  - Removed local `logging.basicConfig` + `RotatingFileHandler` stack.
  - Switched to core logger:
    - `api_logger = get_logger("wizard", category="api-server", name="api-server")`
  - Updated request/response/error middleware logging to structured `ctx` payloads.
- Migrated vibe utility logger setup:
  - `vibe/core/utils.py`
  - `apply_logging_config()` now routes to core logger contract.
  - Removed rotating-file handler setup from this module; fallback is now a null-handler stdlib logger only.
- Added/updated tests:
  - `core/tests/logging_contract_phase2_test.py`
    - Source-level contract test for `server_modular` migration (no `RotatingFileHandler`/`basicConfig`, core logger import present).
    - Source-level contract test for `vibe.core.utils` migration (no `RotatingFileHandler`).
    - Runtime sink test for `vibe.core.utils` logger routing into core JSONL sink.

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
  core/tests/logging_contract_phase2_test.py \
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

Result: `29 passed`.

## Remaining Work

- Sweep downstream tools/workflows that still parse old plain-text rotating logs and migrate them to JSONL reader/export adapters under `memory/logs/udos`.
