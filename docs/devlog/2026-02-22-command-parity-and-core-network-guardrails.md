# 2026-02-22: Command Parity + Core Network Guardrails

## Summary

Implemented the next critical-juncture guardrails from `docs/roadmap.md`:

- Added command-surface parity checks across:
  - dispatcher command list
  - command contract file (`core/config/ucode_command_contract_v1_3_20.json`)
  - prompt registry (`core/input/command_prompt.py`)
- Added static core networking boundary checks:
  - freeze network-capable imports to an explicit allowlist of existing files
  - enforce removal of public DNS probe literal in TUI core path
- Updated contract file to close drift:
  - added `MODE`, `STATUS`, `TIDY`, `UCODE` to `v1.3.20` command contract
- Replaced non-loopback probe in `core/tui/ucode.py`:
  - `1.1.1.1:53` probe removed
  - now checks loopback-local wizard/ollama ports only

## Files Changed

- `core/config/ucode_command_contract_v1_3_20.json`
- `core/tests/command_surface_parity_contract_test.py`
- `core/tests/core_network_boundary_contract_test.py`
- `core/tui/ucode.py`
- `docs/roadmap.md`

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/command_surface_parity_contract_test.py \
  core/tests/core_network_boundary_contract_test.py \
  core/tests/command_catalog_coverage_test.py \
  core/tests/dispatch_rc_scope_contract_test.py \
  core/tests/web_home_proxy_handler_test.py \
  core/tests/vibe_network_service_integration_test.py -q
```

Result: `21 passed`.
