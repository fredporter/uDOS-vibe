# Cycle D Full Sweep + Warning Triage

Date: 2026-02-23
Command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot
```

## Result (post-fix clean-room runner)

- passed: 1946
- failed: 5
- errors: 0
- skipped: 3
- warnings: 2

## Failure/Error Buckets

- `tests/core/test_teleport_git.py`
  - non-repo detection behavior mismatch in `GitRepository.is_supported()` / `get_info()`.
- `core/tests/config_sync_runtime_env_test.py`
  - runtime env precedence mismatch in `USER_NAME` and `MISTRAL_API_KEY` fallback cases.
- `core/tests/path_service_test.py`
  - `find_repo_root` nested start path behavior mismatch.

## Warning Triage

- All warnings are from:
  - `vibe/core/tools/ucode/specialized.py`
- Warning text:
  - Pydantic field name `validate` in `ImportArgs` shadows a `BaseModel` attribute.
- Impact:
  - non-fatal warning; does not fail tests.
- Recommended follow-up:
  - rename `validate` field to a non-reserved name (for example `validate_input`) with alias preservation if wire compatibility is needed.

## Test Runner Structure Updates Applied

- Added canonical profile test runner:
  - `scripts/run_pytest_profile.sh`
- Updated CI workflow to use shared runner and remove redundant explicit target duplication:
  - `.github/workflows/ci-profiles.yml`
- Updated CI matrix how-to to match shared runner targets:
  - `docs/howto/CI-TEST-MATRIX.md`
- Added clean-room env unsets in the shared runner to reduce workstation env bleed into tests.
