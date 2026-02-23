# GA2: uHOME + Home Assistant Bridge Routes

Date: 2026-02-23
Status: Completed

## Scope

Implement the Wizard HA bridge API surface required by the
`Pre-v1.5 Stable: uHOME + Home Assistant Integration` milestone.

## What Changed

### New: `wizard/services/home_assistant_service.py`

- `HomeAssistantService` — bridge service class.
- `is_enabled()` — reads `ha_bridge_enabled` from WizardConfig; defaults to `False` (bridge off by default).
- `status()` — returns bridge version, enabled flag, and allowlist size.
- `discover()` — returns 5 canonical uDOS entity descriptors: system, tuner, dvr, ad_processing, playback.
- `execute_command(command, params)` — validates against a strict `_COMMAND_ALLOWLIST` (12 commands), dispatches to handler or raises `ValueError` for unlisted commands.
- `_COMMAND_ALLOWLIST` — explicit safe set: `uhome.tuner.*`, `uhome.dvr.*`, `uhome.ad_processing.*`, `uhome.playback.*`, `system.info`, `system.capabilities`.
- uHOME commands return a `stub` status response (full uHOME service wiring is GA3 scope).

### New: `wizard/routes/home_assistant_routes.py`

Three routes registered under `/api/ha`:

| Method | Path | Auth | Behaviour |
|--------|------|------|-----------|
| GET | `/api/ha/status` | None | Always responds; returns `disabled` when bridge is off |
| GET | `/api/ha/discover` | auth_guard | Returns entity list; 503 if bridge disabled |
| POST | `/api/ha/command` | auth_guard | Executes allowlisted command; 400 for unknown command; 503 if disabled |

### Modified: `wizard/server.py`

HA router registered immediately after `publish_routes` in `_setup_routes()`.

### Dev Infrastructure (logged here for record)

- `.claude/launch.json` created with wizard-server, dashboard-dev, and web-admin-dev configurations.
- `web-admin/package.json` dev scripts updated: `svelte-kit dev` → `vite dev` (SvelteKit 1.x compatibility).

## Tests Run

```
wizard/tests/home_assistant_routes_test.py  10 passed in 1.65s
```

Test coverage:
- `test_status_when_disabled` — status endpoint returns `disabled` + `enabled: false`.
- `test_status_when_enabled` — status returns `ok` + `enabled: true`.
- `test_discover_when_disabled_returns_503` — correct 503 + detail message.
- `test_discover_when_enabled_returns_entities` — entity list contains expected IDs.
- `test_command_when_disabled_returns_503` — command blocked when bridge off.
- `test_command_not_in_allowlist_returns_400` — rejection with `allowlist` in detail.
- `test_command_system_info` — allowlisted system command executes.
- `test_command_system_capabilities` — returns full allowlist.
- `test_command_uhome_stub` — uHOME command returns stub response.
- `test_command_missing_command_field_returns_422` — Pydantic validation.

## Remaining Risk

- uHOME commands return stub responses; full uHOME service wiring is deferred to GA3.
- HA bridge remains disabled by default; must be opted into via `ha_bridge_enabled` in Wizard config.
- No WebSocket HA event bus yet (defined in `bridge.json` as `ws://localhost:8765/ws/ha`) — deferred to GA4 (Wizard networking/beacon stabilization).

## Exit Condition

GA2 complete. Roadmap advanced; GA3 (Sonic Screwdriver standalone uHOME packaging) is next.
