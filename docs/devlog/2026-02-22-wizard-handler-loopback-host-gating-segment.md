# 2026-02-22: Wizard Handler Loopback Host Gating Segment

## Summary

Hardened Wizard command host resolution boundary in core command surface:

- Updated `core/commands/wizard_handler.py`
  - Added loopback host allowlist (`127.0.0.1`, `::1`, `localhost`)
  - `_wizard_connect_host()` now:
    - maps wildcard binds (`0.0.0.0`, `::`) to `127.0.0.1`
    - allows loopback hosts
    - blocks non-loopback hosts and coerces to `127.0.0.1` with warning log

This prevents non-loopback Wizard host config values from leaking into core runtime network targets.

## Tests Added

- `core/tests/wizard_handler_boundary_test.py`
  - allows expected loopback host forms
  - blocks non-loopback host values
  - verifies `_wizard_urls()` emits loopback URLs when config host is remote

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/wizard_handler_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py \
  core/tests/ucode_setup_network_boundary_test.py -q
```

Result: `11 passed`.
