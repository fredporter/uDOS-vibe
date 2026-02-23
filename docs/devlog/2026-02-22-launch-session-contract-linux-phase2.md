# Launch Session Contract Phase 2 (Linux Wrapper Adapter)

Date: 2026-02-22

## Summary

Completed launch/session contract unification for Linux wrapper flows by adding a dedicated Sonic Linux launcher adapter service and platform API routes that emit the same canonical lifecycle/session state as Windows/media wrappers.

## Changes

- Added Linux launcher adapter:
  - `wizard/services/sonic_linux_launcher_service.py`
  - Uses canonical launch state writer: `wizard/services/launch_session_service.py`
  - Canonical target/mode/launcher contract: `alpine-core-linux-gui` + `gui` + `udos-gui`
  - Lifecycle transitions:
    - `start|restart`: `planned -> starting -> ready`
    - `stop`: `planned -> stopping -> stopped`
  - Protocol parsing: `openrc|direct`
  - Workspace handoff persisted in session/state payloads
  - Optional command execution boundary (`execute: bool`) with captured exit/error fields
- Added Linux platform routes in `wizard/routes/platform_routes.py`:
  - `GET /api/platform/sonic/linux/launcher`
  - `POST /api/platform/sonic/linux/launcher/action`
- Added tests:
  - `wizard/tests/sonic_linux_launcher_service_test.py`
  - `wizard/tests/sonic_platform_linux_launcher_test.py`

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
  wizard/tests/sonic_linux_launcher_service_test.py \
  wizard/tests/sonic_platform_linux_launcher_test.py \
  wizard/tests/launch_session_service_test.py \
  wizard/tests/sonic_platform_windows_launcher_test.py \
  wizard/tests/sonic_platform_media_console_test.py -q
```

Result: `10 passed`.

## Notes

- This phase keeps runtime-safe defaults by not executing host launcher actions unless explicitly requested (`execute=true`).
- Distribution shell script integration can now consume the same session artifacts under `memory/wizard/launch/*.json` in a follow-up hardening pass.
