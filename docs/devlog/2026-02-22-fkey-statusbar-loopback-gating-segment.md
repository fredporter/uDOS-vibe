# 2026-02-22: FKey/StatusBar Loopback Gating Segment

## Summary

Extended core TUI loopback boundary enforcement to interactive utility surfaces:

- `core/tui/fkey_handler.py`
  - added loopback allowlist for Wizard host resolution
  - `_wizard_connect_host()` now coerces non-loopback hosts to `127.0.0.1`
  - consolidated socket probe logic into `_is_wizard_port_open()`
- `core/tui/status_bar.py`
  - added loopback allowlist
  - `_check_server()` now rejects non-loopback hosts (`UNKNOWN`) and probes only loopback targets

## Tests Added

- `core/tests/fkey_status_bar_boundary_test.py`
  - non-loopback host blocked in FKey Wizard host resolution
  - FKey Wizard URLs enforce loopback
  - status bar server probe rejects non-loopback host

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/fkey_status_bar_boundary_test.py \
  core/tests/wizard_handler_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py -q
```

Result: `8 passed`.
