# 2026-02-23 I6 Kickoff: Sonic Alias Retirement Checks (Slice 1)

## Scope

Start I6 from `docs/roadmap.md` by adding explicit, testable control over legacy Sonic alias routes while preserving canonical `/sync/*` endpoints.

## Changes

- Updated `wizard/routes/sonic_plugin_routes.py`:
  - Added `UDOS_SONIC_ENABLE_LEGACY_ALIASES` flag (default enabled).
  - Added `GET /api/sonic/aliases/status` returning:
    - `legacy_aliases_enabled`
    - `retirement_target`
  - Legacy alias routes now return `410` with canonical route metadata when alias mode is disabled:
    - `/api/sonic/rescan`
    - `/api/sonic/rebuild`
    - `/api/sonic/sync`
    - `/api/sonic/export`
    - `/api/sonic/db/status`
    - `/api/sonic/db/rebuild`
    - `/api/sonic/db/export`
- Updated `wizard/tests/sonic_plugin_alias_routes_test.py`:
  - existing compatibility mode assertions retained
  - added retired-mode assertions for `410` alias behavior and canonical route guidance

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
  wizard/tests/sonic_plugin_alias_routes_test.py
```

## Result

- PASS: `2 passed`
- FAIL: `0`
- WARN: `0`

## Next I6 Slices

- Add Sonic schema/adapter parity checks across SQL + JSON schema + adapter payload types.
- Convert route-level alias compatibility into a measured deprecation plan for freeze (non-blocking diagnostics before default retirement).
