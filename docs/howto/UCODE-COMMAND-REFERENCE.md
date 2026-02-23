# uCODE Command Reference

Version: Core v1.3.20+
Updated: 2026-02-22

This guide covers uDOS commands (ucode) which are **backend services**, not UI features.

Offline operations runbook:
- `docs/howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md`

## Multi-Context Command Execution

uDOS commands execute in multiple contexts:

### 1. Vibe CLI Interactive (Primary)
```bash
vibe
# User: "show me the map"
# → Routes to ucode_map skill via MCP
```

### 2. Vibe Bash Tool
```bash
vibe
# User: "/bash ucode MAP"
# → Executes shell command via Vibe
```

### 3. Shell/Script Execution
```bash
# Direct execution
ucode MAP

# Background task
ucode SETUP WIZARD --background

# Check progress
ucode SETUP CHECK --vibe
ucode STATUS TASK_ID
```

### 4. Python API (Internal)
```python
from core.services.command_dispatch_service import CommandDispatchService
dispatcher = CommandDispatchService()
result = dispatcher.dispatch("MAP")
```

---

## Command Categories

This guide is organized by:
- TypeScript-backed command paths (Node runtime required, /core/tsrun)
- Python ucode command surface (core dispatcher, /core stdlib-only)
- Wizard commands (networking, GUI, packaging, /wizard)
- Extension commands (/extensions, /sonic)

## Environment Configuration

### Keymap Profiles (Wizard Web UI)
- Dashboard page: `Wizard -> Hotkeys`
- API: `GET /api/ucode/hotkeys`, `GET /api/ucode/keymap`, `POST /api/ucode/keymap`
- Profiles: `mac-obsidian`, `mac-terminal`, `linux-default`, `windows-default`

### Core Environment Variables
```bash
# Keymap
export UDOS_KEYMAP_PROFILE=mac-obsidian
export UDOS_KEYMAP_OS=mac  # mac|linux|windows
export UDOS_KEYMAP_SELF_HEAL=1

# Message theming (terminal output only)
export UDOS_THEME=<theme>
export UDOS_MESSAGE_THEME=fantasy  # Not TUI-specific
export UDOS_MAP_LEVEL=dungeon      # Spatial context, not UI
```

**Note**: Former `UDOS_TUI_*` variables renamed to clarify they control backend message formatting, not UI rendering. Vibe CLI is the active interactive interface.

Legacy pre-`vibe-cli` interactive references were composted here:
- `docs/.compost/tui-legacy-2026-02/TUI-MIGRATION-PLAN.md`
- `docs/.compost/tui-legacy-2026-02/VIBE-UCLI-INTEGRATION-GUIDE.md`

Active migration notes for current operators:
- `docs/howto/MIGRATION-NOTES-LEGACY-FLOWS.md`

## Selector and Input Contract

Selector behavior for `/ucode` addon commands is standardized by:

- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md`

Readiness and validation workflow:

- `docs/howto/UCODE-SELECTOR-READINESS.md`
- `./bin/check-ucode-selectors.sh`

Required behavior for selector-enabled commands:

1. Detect interactive mode first (`isatty` / shell TTY).
2. Prefer selector tools in interactive mode:
   - file selection: `fzf` + `fd`
   - menu selection: `gum`
   - python prompts: `PyInquirer` or `pick`
3. Fallback to non-interactive flags when selectors are unavailable or TTY is absent (`--file`, `--files`, `--choice`).
4. Keep command outputs shell-safe and scriptable.

## TypeScript Command Set

These commands execute via TS/Node runtime components.

- `RUN --ts <file> [section_id]`
- `RUN --ts PARSE <file>`
- `RUN --ts DATA LIST`
- `RUN --ts DATA VALIDATE <id>`
- `RUN --ts DATA BUILD <id> [output_id]`
- `RUN --ts DATA REGEN <id> [output_id]`
- `READ --ts <file>`
- `STORY <file>`
- `STORY PARSE <file>`
- `STORY NEW <name>`
- `SCRIPT RUN <name>`
- `DRAW PAT LIST`
- `DRAW PAT CYCLE`
- `DRAW PAT TEXT "<text>"`
- `DRAW PAT <pattern-name>`
- `DRAW --py PAT <...>` (Python-backed pattern renderer)
- `DRAW MD <mode>` or `DRAW --md <mode>` (markdown fenced diagram output)
- `DRAW --save <file.md> <mode>` (persist diagram output)
- `GRID <calendar|table|schedule|map|dashboard|workflow> [options]`
- `VERIFY`

## Script Policy (Mobile Default)

uDOS-flavored markdown scripts now run in mobile-safe mode by default.

- Default: script fences cannot execute stdlib ucode command lines.
- Explicit opt-in: add `allow_stdlib_commands: true` in markdown frontmatter.
- Applies to `RUN`, `SCRIPT RUN`, and system script execution paths.

Example frontmatter:

```yaml
---
title: Startup Script
allow_stdlib_commands: true
---
```

## Python ucode Commands (Core Surface)

Current dispatch registry (54 commands) is defined in:
- `core/config/ucode_command_contract_v1_3_20.json`
- `core/services/command_dispatch_service.py` (runtime matcher)

Contract command set:

`ANCHOR`, `BAG`, `BINDER`, `CLEAN`, `COMPOST`, `CONFIG`, `DESTROY`, `DEV`, `DRAW`, `EMPIRE`, `FILE`, `FIND`, `GHOST`, `GOTO`, `GRAB`, `GRID`, `HEALTH`, `HELP`, `LIBRARY`, `LOAD`, `LOGS`, `MAP`, `MIGRATE`, `MODE`, `MUSIC`, `NPC`, `PANEL`, `PLACE`, `PLAY`, `READ`, `REBOOT`, `REPAIR`, `RESTART`, `RULE`, `RUN`, `SAVE`, `SCHEDULE`, `SCHEDULER`, `SCRIPT`, `SETUP`, `SKIN`, `SONIC`, `SPAWN`, `TALK`, `TELL`, `THEME`, `TOKEN`, `UID`, `UNDO`, `USER`, `VERIFY`, `VIEWPORT`, `WIZARD`

Notes:
- Legacy `NEW` and `EDIT` are consolidated into `FILE NEW` and `FILE EDIT`.
- `UCODE` offline utility commands (`UCODE DEMO|DOCS|SYSTEM|CAPABILITIES|PLUGIN|UPDATE`) are available in current runtime flow.
- `UCODE SYSTEM INFO` includes minimum-spec validation for `2 cores / 4.0 GB RAM / 5.0 GB free storage`.
- `UCODE SYSTEM INFO` includes a first field-validation round marker with local sample size and rebaseline targets.
- `UCODE PLUGIN INSTALL <name>` creates a local plugin scaffold entry for capability discovery (`UCODE CAPABILITIES`).
- `UCODE METRICS` reports local-only usage metrics from `~/.vibe-cli/ucode/metrics/` (no network export).

### Maintenance Storage Policy (v1.3.13+)

- `BACKUP` writes to `/.compost/<date>/backups/<scope>/`
- `RESTORE` and `UNDO` read latest from `/.compost/<date>/backups/<scope>/`
- `TIDY` and `CLEAN` move files to `/.compost/<date>/trash/<timestamp>/<scope>/`
- `COMPOST` migrates older local dirs (`.archive`, `.backup`, `.tmp`, `.temp`) into `/.compost/<date>/archive/...`

## Wizard-Owned Flows

Provider/integration/full network checks are Wizard-owned.

```bash
WIZARD PROV LIST
WIZARD PROV STATUS
WIZARD INTEG status
WIZARD CHECK
```

## SONIC Parity Quick Reference

Core command:
- `SONIC STATUS`
- `SONIC SYNC [--force]`
- `SONIC PLAN ...`
- `SONIC RUN ... --confirm`

Wizard API equivalents:
- `GET /api/platform/sonic/status`
- `POST /api/sonic/db/rebuild` (or `POST /api/sonic/sync`)
- `POST /api/platform/sonic/build`

## Removed Top-Level Commands

These are removed from the canonical command surface:

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`

Migration targets:

- `SHAKEDOWN` -> `HEALTH` or `VERIFY` (core), `WIZARD CHECK` (full checks)
- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`
- `INTEGRATION ...` -> `WIZARD INTEG ...`
- `PROVIDER ...` -> `WIZARD PROV ...`

## Quick Checks

```bash
HEALTH
VERIFY
FILE SELECT --files readme.md,docs/roadmap.md
UCODE DEMO LIST
UCODE DOCS --query reference
UCODE SYSTEM INFO
UCODE CAPABILITIES --filter core
UCODE PLUGIN LIST
UCODE METRICS
RULE LIST
DRAW PAT LIST
RUN DATA LIST
WIZARD CHECK
```

## FILE SELECT Examples

```bash
# Non-interactive single file
FILE SELECT --file readme.md

# Non-interactive multi-file
FILE SELECT --files readme.md,docs/roadmap.md

# Interactive selector in a workspace
FILE SELECT --workspace @sandbox

# Interactive single-select
FILE SELECT --workspace @vault --single
```

## GRID Workflow Quick Example

Use the tracked sample payload under `memory/system/`:

```bash
GRID WORKFLOW --input memory/system/grid-workflow-sample.json
```

Other canonical GRID samples:

```bash
GRID CALENDAR --input memory/system/grid-calendar-sample.json
GRID TABLE --input memory/system/grid-table-sample.json
GRID SCHEDULE --input memory/system/grid-schedule-sample.json
GRID MAP --input memory/system/grid-overlays-sample.json
```

## Message Themes (Terminal Output)

uCode message wording can be lightly themed for spatial/map consistency.

- Scope: Terminal message formatting only (not GUI/CSS/webview styling)
- Base env: `UDOS_THEME=<theme>`
- Message theme: `UDOS_MESSAGE_THEME=fantasy|role-play|explorer|scientist|pilot|captain-sailor|pirate|adventure|scavenge-hunt|traveller|dungeon|foundation|galaxy|stranger-things|lonely-planet|doomsday|hitchhikers`
- Map-level hint: `UDOS_MAP_LEVEL=dungeon|foundation|galaxy|...`

## Z-Layer + TOYBOX Gameplay Lens

Use this pattern when changing gameplay lens:

```bash
# TOYBOX dungeon profile + dungeon-style messages
PLAY TOYBOX SET hethack
export UDOS_MAP_LEVEL=dungeon
export UDOS_MESSAGE_THEME=dungeon

# TOYBOX galaxy profile + galaxy-style messages
PLAY TOYBOX SET elite
export UDOS_MAP_LEVEL=galaxy
export UDOS_MESSAGE_THEME=pilot
```

Notes:
- `PLAY TOYBOX SET ...` changes gameplay profile state
- `UDOS_MAP_LEVEL` and `UDOS_MESSAGE_THEME` control terminal message wording
- z/elevation (`-Zz`, `z_min`, `z_max`, stairs/ramps/portals) is **spatial/map data** (game layer), not UI styling
- "Z-Layer" refers to vertical spatial coordinates in gameplay, not rendering layers
- `PLAY LENS STATUS` surfaces readiness + recommendation hints from progression requirements
- `PLAY LENS SCORE [lens]` returns lens-specific scorecards (variables + scoped metrics + tier)
- `PLAY LENS CHECKPOINTS [lens]` returns progression checkpoints and next-blocked hint
- `PLAY PROFILE STATUS [--group <id>] [--session <id>]` resolves user variables with optional overlay scopes
- `PLAY PROFILE GROUP|SESSION SET|CLEAR ...` manages optional group/session overlay values
- `SKIN CHECK` and `SKIN STATUS` may return advisory `policy_flag` values (`skin_lens_mismatch`, `skin_lens_unmapped`, `skin_lens_progression_drift`) without enforcement in dev rounds
- `SKIN SHOW <name>` reports explicit gameplay metadata contract validity from `themes/*/theme.json`
