# 2026-02-22: Core Service Loopback Gating Segment

## Summary

Extended core networking boundary enforcement to additional services:

- `core/services/config_sync_service.py`
  - `sync_env_to_wizard()` now rejects non-loopback `wizard_api_url` targets.
  - migrated API call from `requests.post` to stdlib `http_post` (`core.services.stdlib_http`).
- `core/services/dev_state.py`
  - added loopback sanitizer for `WIZARD_BASE_URL` before `/api/dev/status` call.
  - migrated network call from `requests.get` to stdlib `http_get`.

## Tests Added

- `core/tests/config_sync_network_boundary_test.py`
  - blocks non-loopback wizard sync target
  - verifies successful local loopback sync call shape
- `core/tests/dev_state_boundary_test.py`
  - non-loopback base URL falls back to loopback
  - `get_dev_active()` uses loopback fallback URL

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/config_sync_runtime_env_test.py \
  core/tests/config_sync_network_boundary_test.py \
  core/tests/dev_state_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py -q
```

Result: `9 passed`.

## Remaining Scope

Networking cleanup is still in progress for other core paths that include direct networking behavior (for example portions of setup/self-heal flows). Those should be migrated behind the same loopback/Wizard boundary pattern.
