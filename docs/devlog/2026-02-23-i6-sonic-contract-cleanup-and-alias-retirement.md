# 2026-02-23 I6 Complete: Sonic Contract Cleanup + Alias Retirement Checks

## Scope

Complete I6 from `docs/roadmap.md`: Sonic schema/adapter contract cleanup and alias retirement readiness checks.

## Delivered Across I6 Slices

- Alias retirement control and observability for Sonic plugin routes:
  - `wizard/routes/sonic_plugin_routes.py`
  - env gate: `UDOS_SONIC_ENABLE_LEGACY_ALIASES`
  - `GET /api/sonic/aliases/status`
  - retired aliases return `410` with canonical route guidance when disabled
- Schema contract parity guard:
  - `wizard/services/sonic_schema_contract.py`
  - `GET /api/sonic/schema/contract`
  - validates SQL columns/required vs JSON properties/required
  - validates enum parity (`usb_boot`, `reflash_potential`) with `library.sonic.schemas`
- Adapter payload invariants added to parity guard:
  - adapter payload includes all SQL `devices` columns
  - legacy `usb_boot` normalization path (`yes` -> `native`) remains enforced
- Library alias retirement readiness:
  - `wizard/routes/library_routes.py`
  - env gate: `UDOS_SONIC_ENABLE_LIBRARY_ALIAS`
  - `GET /api/library/aliases/status`
  - `/api/library/integration/sonic` returns `410` with canonical route when alias disabled
- Live dataset contract fix discovered by parity checks:
  - `sonic/datasets/sonic-devices.sql`
  - `year` changed to `INTEGER NOT NULL` to match JSON schema required fields

## Tests Added/Updated

- `wizard/tests/sonic_plugin_alias_routes_test.py`
- `wizard/tests/sonic_schema_contract_test.py`
- `wizard/tests/sonic_library_alias_routes_test.py`

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
  wizard/tests/sonic_library_alias_routes_test.py \
  wizard/tests/sonic_schema_contract_test.py \
  wizard/tests/sonic_plugin_alias_routes_test.py
```

## Result

- PASS: `7 passed`
- FAIL: `0`
- WARN: `0`

## Outcome

- I6 exit condition satisfied: Sonic schema/adapter contract checks are enforced and alias retirement behavior is explicit, controllable, and test-covered.
