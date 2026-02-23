# 2026-02-22: uCODE Wizard Lifecycle stdlib HTTP Segment

## Summary

Completed the next core TUI networking cleanup pass by removing `requests` usage from Wizard lifecycle/status/page helpers:

- Updated `core/tui/ucode.py`:
  - `_wizard_start()`
  - `_wizard_stop()`
  - `_wizard_status()`
  - `_wizard_page()`
- Replaced direct `requests.get(...)` calls with stdlib `http_get(...)` and `HTTPError` handling.
- Preserved behavior for:
  - startup short-circuit when Wizard is already healthy
  - stop verification
  - status output and offline handling
  - page fetch error reporting
- Removed `import requests` from `core/tui/ucode.py` (no remaining `requests` usage in file).

## Tests Added/Updated

- Updated `core/tests/ucode_setup_network_boundary_test.py` with lifecycle/status/page checks:
  - `_wizard_start()` short-circuits on healthy Wizard
  - `_wizard_status()` reports "not running" on connection errors
  - `_wizard_page()` reports HTTP error codes

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/ucode_setup_network_boundary_test.py \
  core/tests/ucode_network_boundary_test.py \
  core/tests/config_sync_network_boundary_test.py \
  core/tests/dev_state_boundary_test.py \
  core/tests/self_healer_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py -q
```

Result: `18 passed`.
