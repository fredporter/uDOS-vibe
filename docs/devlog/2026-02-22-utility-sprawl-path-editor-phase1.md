# Utility Sprawl Reduction: Path + Editor Phase 1

Date: 2026-02-22

## Summary

Implemented phase-1 utility consolidation by introducing a canonical path service and migrating existing root/path/editor helpers to consume it, reducing duplicate root-detection and workspace-path logic.

## Changes

- Added canonical path module:
  - `core/services/path_service.py`
  - Provides:
    - `find_repo_root()`
    - `get_repo_root()` (cached)
    - `clear_repo_root_cache()`
    - `get_memory_root()`
    - `resolve_repo_path()`
  - Enforces `UDOS_HOME_ROOT_ENFORCE=1` policy consistently.
- Refactored core logging root detection:
  - `core/services/logging_api.py`
  - `get_repo_root()` now delegates to canonical path service.
- Refactored wizard path utilities:
  - `wizard/services/path_utils.py`
  - `find_repo_root()` and `get_repo_root()` now delegate to canonical path service.
  - Kept local `_resolve_repo_path()` behavior compatible with monkeypatched `get_repo_root()` tests.
- Refactored editor helper duplication:
  - `core/services/editor_utils.py` now uses canonical path service for repo/memory root.
  - `wizard/services/editor_utils.py` now reuses `core.services.editor_utils.resolve_workspace_path` and `find_nano_binary`.

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
  core/tests/path_service_test.py \
  core/tests/packaging_manifest_service_test.py \
  wizard/tests/path_utils_scheme_test.py \
  wizard/tests/workspace_routes_test.py \
  wizard/tests/sonic_build_service_artifacts_test.py \
  wizard/tests/sonic_linux_launcher_service_test.py \
  wizard/tests/sonic_platform_linux_launcher_test.py \
  wizard/tests/ucode_setup_story_utils_test.py \
  wizard/tests/ucode_ok_mode_utils_test.py -q
```

Result: `29 passed`.

## Remaining Work

- Consolidate broader utility families beyond path/editor (logging helper adapters, json/time/hash wrappers).
- Remove remaining redundant wrapper utilities after call-site migration parity checks.
