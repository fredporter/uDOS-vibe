# Architecture Note — MCP Bridge Implementation

**Version:** v1.4.4+
**Date:** 2026-02-06 (original), 2026-02-22 (updated)
**Status:** Implemented

## Decision

Implemented MCP bridge for Vibe CLI integration:

- `wizard/mcp/mcp_server.py` — stdio MCP server bridging Vibe → uDOS commands
- `.vibe/config.toml` — MCP server registration and tool/skill paths
- Command execution via multiple contexts (Vibe interactive, Vibe bash tool, shell, Python API)

Wizard directory contains both MCP server and optional web admin UI.

## Rationale

- **Vibe-first architecture**: Vibe CLI is exclusive interactive interface; MCP bridge enables AI-powered command routing
- **Multi-context execution**: Commands work in Vibe interactive, Vibe bash tool, shell scripts, and Python API
- **Single command surface**: All contexts route through same CommandDispatcher/command handlers
- **Optional wizard services**: MCP server can run standalone (stdio) or with web admin UI

## Implementation Status

- ✅ MCP server implemented: `wizard/mcp/mcp_server.py`
- ✅ Vibe config committed: `.vibe/config.toml`
- ✅ Command infrastructure preserved: `core/tui/dispatcher.py`, `core/commands/`
- ✅ Multi-context execution documented: [TUI-Vibe-Integration.md](TUI-Vibe-Integration.md)
- ✅ Background task workflow: `--background` flag, `STATUS`/`LOGS` commands

## References

- [TUI-Vibe-Integration.md](TUI-Vibe-Integration.md) — Multi-context execution patterns
- [UCODE-COMMAND-REFERENCE.md](../howto/UCODE-COMMAND-REFERENCE.md) — Complete command reference
- [ARCHITECTURE.md](../ARCHITECTURE.md) — Repository structure overview

