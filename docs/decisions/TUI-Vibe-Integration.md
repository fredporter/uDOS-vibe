# Vibe CLI Integration Decision (v1.4.6)

## Status

Active.

Vibe CLI is the primary interactive interface for uDOS. Legacy standalone interactive TUI flow is retired.

## Decision Summary

uDOS keeps one interactive lane and multiple execution contexts:

1. `vibe` interactive (primary)
2. Vibe bash tool (`/bash ucode ...`)
3. direct shell execution (`ucode ...`) for scripts/automation

Core command infrastructure remains intact; only the interactive entry point is consolidated.

## Architecture

```text
Vibe CLI
  -> Vibe ucode tool definitions (vibe/core/tools/ucode/*)
  -> MCP protocol
  -> Wizard MCP server (wizard/mcp/mcp_server.py)
  -> uDOS command dispatch (core/services/command_dispatch_service.py / core/tui/dispatcher.py)
  -> command handlers (core/commands/*, wizard-owned services where applicable)
```

## Scope Boundaries

### Interactive Ownership

- `vibe` owns interactive UX and command mediation.
- uDOS commands remain backend services and execution contracts.

### TUI Text Operations vs Wizard GUI

- Terminal text behavior (selectors, file pickers, input/output handlers) is a Core/Vibe text-operations concern.
- Wizard dashboard visuals are GUI concerns and not normative for terminal command behavior.
- Reference decision: `TERMINAL-STYLING-v1.3.md` (rewritten as Terminal Text Operations Decision).

## Execution Contexts

### 1. Vibe CLI Interactive (primary)

Use natural language; Vibe routes to uDOS tools/commands via MCP.

### 2. Vibe Bash Tool

Use `/bash ucode COMMAND` for direct shell-style execution from inside Vibe.

### 3. Shell / Script Execution

Use `ucode COMMAND` directly for automation, CI, cron, and background operations.

## Preserved vs Retired

### Preserved

- command dispatcher and command handlers
- command contracts and aliases
- shell-safe output contracts
- MCP gateway and tool routing

### Retired

- legacy standalone interactive TUI as primary operator surface
- duplicated UI runtime pathways that competed with `vibe`

## Configuration Model

- Vibe-owned local config/env: `~/.vibe/config.toml`, `~/.vibe/.env`
- uDOS extends tool paths/server bindings without replacing standard Vibe behavior
- non-identity secrets remain Wizard-keystore managed when Wizard is available

## Operational Notes

- Use `vibe` for interactive operations.
- Use `ucode ...` for scripts/automation/non-interactive pipelines.
- Keep command examples aligned with `docs/howto/UCODE-COMMAND-REFERENCE.md`.

## Migration Note

Legacy flow migration context is archived; current operators should use active how-to/spec docs.

## Related Documents

- `docs/howto/VIBE-MCP-INTEGRATION.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/specs/VIBE-UCODE-PROTOCOL-v1.4.4.md`
- `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md`
- `docs/roadmap.md`
