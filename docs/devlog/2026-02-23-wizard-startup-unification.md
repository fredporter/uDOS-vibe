# 2026-02-23 Wizard Startup Unification

## Summary

Reduced startup-path drift by unifying daemon lifecycle control behind the core Wizard process manager.

## Changes

- Added `core/services/wizard_daemon_cli.py` as the canonical CLI surface for:
  - `start`, `stop`, `restart`, `status`, `health`, `logs`
- Converted `bin/wizardd` into a thin wrapper:
  - `uv run -m core.services.wizard_daemon_cli "$@"`
- Updated MCP gateway local auto-start path:
  - `wizard/mcp/gateway.py` now starts local Wizard through `bin/wizardd start` instead of duplicating PID/process logic.
- Updated stale startup command references in runtime config:
  - `wizard/services/port_manager.py`
  - `wizard/config/port_registry.json`
  - `core/commands/dev_mode_handler.py`

## Outcome

Wizard startup, status, and stop flows now share one core implementation path, reducing drift between TUI, proxy, MCP, and shell daemon operations.
