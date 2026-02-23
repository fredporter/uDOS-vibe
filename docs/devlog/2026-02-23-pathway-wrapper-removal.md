# 2026-02-23 Pathway Wrapper Removal

## Summary

Removed remaining legacy compatibility wrappers so canonical modular entrypoints are the only supported runtime pathways for first-edition release stabilization.

## Removed files

- `distribution/plugins/api/server.py`
- `wizard/mcp/server.py`
- `wizard/services/sonic_service.py`

## Canonical paths

- API runtime: `distribution/plugins/api/server_modular.py`
- MCP runtime: `wizard/mcp/mcp_server.py`
- Sonic Wizard service: `wizard/services/sonic_plugin_service.py`

## Test and doc updates

- Updated wrapper tests to validate removal and canonical path presence:
  - `wizard/tests/legacy_entrypoint_wrapper_test.py`
- Replaced legacy Sonic compatibility test with canonical service contract test:
  - `wizard/tests/sonic_plugin_service_contract_test.py`
- Updated docs/package snapshots:
  - `distribution/plugins/api/README.md`
  - `wizard/mcp/README.md`
  - `wizard/mcp/gateway.py`
  - `distribution/plugins/api/services/executor.py`
  - `distribution/test-packages/udos-api.tcz.list`
  - `docs/roadmap.md`
