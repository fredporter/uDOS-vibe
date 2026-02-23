# Core

Version: v1.4.4+
Last Updated: 2026-02-22

Core is the offline/local execution layer for uDOS.

## What Core owns

- Local TUI command dispatch
- Filesystem/state operations
- Offline diagnostics
- TypeScript runtime orchestration for local features

## Core command highlights

- Health checks: `HEALTH`, `VERIFY`, `REPAIR`
- Pattern path: `DRAW PAT ...`
- Dataset path: `RUN --ts DATA ...`
- Runtime parse path: `READ --ts ...` / `RUN --ts PARSE ...`
- Canonical UX commands: `PLACE`, `SEND`, `GHOST`, `TOKEN`
- Gameplay profile path: `GAMEPLAY TOYBOX LIST|SET <profile>`

Examples:

```bash
HEALTH
VERIFY
DRAW PAT LIST
RUN --ts DATA LIST
READ --ts memory/system/startup-script.md
```

## Core boundary

Core remains offline-first and does not own provider/integration/full-system network checks.

Removed top-level core commands (hard fail):

- `SHAKEDOWN`
- `INTEGRATION`
- `PROVIDER`
- `PATTERN` (removed in v1.4.3)
- `DATASET`

Legacy command families replaced by canonical surfaces:

- `WORKSPACE` / `TAG` / `LOCATION` -> `PLACE`
- `TALK` / `REPLY` -> `SEND`

## Where provider/integration checks live

Use Wizard surfaces:

```bash
WIZARD CHECK
WIZARD PROV STATUS
WIZARD INTEG status
```

## TUI Z-layer and Theme/Layer Switching

Core supports message-level theme switching for map-level consistency.

- Spatial z/elevation data: `-Zz`, `z`, `z_min`, `z_max`, `stairs`, `ramps`, `portals`
- Message-level hints:
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=<theme>`
- Gameplay profile switch:
  - `GAMEPLAY TOYBOX SET hethack|elite`

See: [TUI Z-Layer, TOYBOX, and Theme Switching](TUI-Z-Layer-and-TOYBOX.md)

## Architecture

```text
core/
  commands/      # Core handlers
  tui/           # TUI + dispatcher
  runtime/       # TS runtime helpers (draw/data/script)
  config/        # command contract + local config
```
