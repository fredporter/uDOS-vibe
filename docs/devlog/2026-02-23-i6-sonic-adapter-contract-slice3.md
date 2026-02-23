# 2026-02-23 I6 Slice 3: Sonic Adapter Contract Invariants

## Scope

Continue I6 by extending Sonic schema contract checks to include adapter payload invariants, not just SQL/JSON/Python enum parity.

## Changes

- Extended `wizard/services/sonic_schema_contract.py` contract output with adapter checks:
  - verifies adapter payload includes all SQL device columns
  - verifies legacy `usb_boot` normalization (`yes` -> `native`) through adapter path
- Added adapter invariant assertions in `wizard/tests/sonic_schema_contract_test.py`:
  - aligned fixture contract includes no missing SQL columns in adapter payload
  - legacy USB normalization check is true
  - repo-level parity guard now also asserts adapter SQL-column completeness

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  wizard/tests/sonic_schema_contract_test.py \
  wizard/tests/sonic_plugin_alias_routes_test.py
```

## Result

- PASS: `5 passed`
- FAIL: `0`
- WARN: `0`

## Remaining I6 Work

- Finish alias-retirement readiness checks across remaining Sonic entrypoints outside `/api/sonic` compatibility shims.
- Once complete, update RC1 Sonic freeze-blocker criterion and mark I6 done.
