# 2026-02-22: Core Network Literal Target Guardrail Segment

## Summary

Strengthened CI boundary enforcement in `core/tests/core_network_boundary_contract_test.py`:

- Added static AST-based guardrail that scans network-capable core modules and rejects:
  - non-loopback literal HTTP targets used in network call sites
  - non-loopback literal socket host targets used in connect calls
- Kept scope intentionally narrow to executable call targets (not generic string literals), reducing false positives from help/docs text.

## Test Coverage

- `test_core_literal_network_targets_are_loopback_only()` now enforces literal target policy.
- Existing guards remain:
  - network import allowlist freeze
  - no public DNS probe literal in core TUI

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/core_network_boundary_contract_test.py \
  core/tests/wizard_handler_boundary_test.py \
  core/tests/fkey_status_bar_boundary_test.py -q
```

Result: `9 passed`.
