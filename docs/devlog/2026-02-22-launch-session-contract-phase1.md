# Launch Session Contract Phase 1 (Wizard Sonic Wrappers)

Date: 2026-02-22

## Summary

Implemented phase-1 launch/session contract unification for Wizard Sonic wrappers by introducing a canonical launch session state service and wiring existing Windows/media wrappers through it.

## Changes

- Added canonical launch/session service:
  - `wizard/services/launch_session_service.py`
  - Contract fields: `{target, mode, launcher, workspace, profile_id, auth}`
  - State namespace: `memory/wizard/launch/*.json`
  - Lifecycle states: `planned -> starting -> ready -> stopping -> stopped -> error`
- Updated `wizard/services/sonic_windows_launcher_service.py`:
  - `set_mode()` now creates/transitions launch sessions (`planned -> starting -> ready`)
  - Persisted `session_id` and `state` in Sonic state output
  - `get_status()` now exposes launch namespace and current session id
- Updated `wizard/services/sonic_media_console_service.py`:
  - `start()` now transitions (`planned -> starting -> ready`)
  - `stop()` now transitions (`planned -> stopping -> stopped`)
  - Persisted `session_id` and `state` and exposed them in status
- Added tests:
  - `wizard/tests/launch_session_service_test.py`

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
  wizard/tests/launch_session_service_test.py \
  wizard/tests/sonic_platform_windows_launcher_test.py \
  wizard/tests/sonic_platform_media_console_test.py -q
```

Result: `5 passed`.

## Remaining Work

- Migrate Linux launch wrappers/adapters to the same launch/session contract.
- Normalize script adapters to emit/read the same canonical request/state payload.
