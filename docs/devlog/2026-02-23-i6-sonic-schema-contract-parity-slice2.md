# 2026-02-23 I6 Slice 2: Sonic Schema Contract Parity Guard

## Scope

Continue I6 by enforcing parity between Sonic SQL schema, JSON schema, and Wizard adapter contract surfaces.

## Changes

- Added contract validation service:
  - `wizard/services/sonic_schema_contract.py`
- Validations implemented:
  - SQL `devices` columns vs JSON schema `properties`
  - SQL required columns (`NOT NULL` + `PRIMARY KEY`) vs JSON schema `required`
  - enum parity for `usb_boot` and `reflash_potential` between JSON schema and `library.sonic.schemas`
- Added Sonic route endpoint:
  - `GET /api/sonic/schema/contract` in `wizard/routes/sonic_plugin_routes.py`
- Added alias contract observability endpoint integration in tests:
  - `wizard/tests/sonic_plugin_alias_routes_test.py`
- Added schema contract tests:
  - `wizard/tests/sonic_schema_contract_test.py`
  - mismatch detection case
  - aligned contract pass case
  - live repo parity guard case
- Fixed live contract drift:
  - Updated `sonic/datasets/sonic-devices.sql` to align with JSON schema required fields:
    - `year INTEGER NOT NULL`

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

- Extend parity coverage to adapter payload invariants beyond enum/field contract checks.
- Complete alias retirement readiness checks across remaining Sonic entry surfaces before marking I6 done.
