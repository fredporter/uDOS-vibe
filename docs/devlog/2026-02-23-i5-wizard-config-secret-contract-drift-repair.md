# 2026-02-23 I5: Wizard Config + Secret Contract Drift Repair

## Scope

Complete I5 from `docs/roadmap.md`: enforce a single admin auth contract across `.env`, `wizard/config/wizard.json`, and Wizard secret store, with startup drift checks, explicit repair actions, and lifecycle tests.

## Changes

- Added canonical contract service:
  - `wizard/services/admin_secret_contract.py`
- Implemented drift detection (`collect_admin_secret_contract`) for:
  - missing `.env` `WIZARD_KEY`
  - missing `.env` `WIZARD_ADMIN_TOKEN`
  - missing `wizard/config/wizard.json` `admin_api_key_id`
  - locked/unreadable secret tomb
  - missing secret entry for `admin_api_key_id`
  - token mismatch between env and secret entry
- Implemented repair flow (`repair_admin_secret_contract`) with explicit behavior:
  - synchronize `.env` key/token + `wizard.json` key id + secret entry
  - preserve existing token when valid
  - recover tomb/key mismatch by controlled tomb reset and reseeding admin token
- Extended local admin-token routes in `wizard/routes/config_admin_routes.py`:
  - `GET /api/admin-token/contract/status`
  - `POST /api/admin-token/contract/repair`
- Added startup drift check in `wizard/server.py`:
  - evaluates contract on app creation
  - stores status on `app.state.admin_secret_contract`
  - logs drift + suggested repair actions if not healthy
- Added operator runbook:
  - `docs/howto/WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md`

## Lifecycle Coverage Added

- `wizard/tests/admin_secret_contract_service_test.py`
  - drift detection for missing/misaligned contract state
  - repair synchronization across env/config/secret store
  - locked-store recovery path (tomb/key mismatch simulation)
- `wizard/tests/config_admin_routes_test.py`
  - contract status + repair route behavior
  - admin token rotation respects configured `admin_api_key_id`

## Validation Commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  wizard/tests/admin_secret_contract_service_test.py \
  wizard/tests/config_admin_routes_test.py
```

## Result

- PASS: `9 passed in 1.71s`
- FAIL: `0`
- WARN: `0`

## Missed-TODO Sweep (Touched Files)

- `wizard/services/admin_secret_contract.py`: no actionable TODO/FIXME markers.
- `wizard/routes/config_admin_routes.py`: no actionable TODO/FIXME markers.
- `wizard/server.py`: no actionable TODO/FIXME markers.
- `docs/howto/WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md`: no actionable TODO/FIXME markers.

## Remaining Risk

- I5 validation is targeted to contract + route flows. Full Wizard profile and full-profile matrix sweeps remain queued under I7 readiness validation.
