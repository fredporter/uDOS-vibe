# TUI Migration Plan: Vibe-Only Architecture

**Date**: 2026-02-22
**Status**: Planning
**Context**: Migration from dual TUI (uCLI + Vibe) to Vibe-only architecture

## Executive Summary

uDOS previously maintained its own TUI (`ucli`/`ucode`) alongside Mistral Vibe CLI integration. As of this version, we use **Vibe CLI exclusively** as the interactive interface. All uDOS commands are now exposed as Vibe skills/tools via the MCP bridge.

This document outlines the plan to:
1. Remove or archive standalone `ucli`/`ucode` TUI code
2. Update documentation to reflect Vibe-only architecture
3. Clean up runtime dependencies
4. Preserve command execution pathways via Vibe tools

---

## Current Architecture Assessment

### ✅ What's Working (Keep)

1. **Vibe CLI Integration** (`vibe/core/tools/ucode/`)
   - Tools: spatial.py, workspace.py, etc.
   - Properly integrated with Vibe's tool discovery
   - All go through MCP server (wizard/mcp/mcp_server.py)

2. **MCP Bridge** (wizard/mcp/)
   - Routes Vibe tool calls → uDOS core commands
   - Phase A offline fallback removed (MCP-only)
   - Status: Production-ready

3. **Core Command Handlers** (core/services/)
   - Command dispatch service
   - Skill mappers
   - All backend logic independent of TUI

### ⚠️ Legacy Components (Evaluate)

1. **Standalone TUI Code** (`core/tui/` - 25 files, ~8000 LOC)
   ```
   core/tui/
   ├── ucli.py              # Legacy interactive REPL
   ├── ucode.py             # Main TUI implementation (~3000 LOC)
   ├── ucli_main.py
   ├── ucode_main.py
   ├── dispatcher.py        # May be used for shell command execution
   ├── renderer.py          # TUI rendering - remove
   ├── status_bar.py        # TUI UI - remove
   ├── file_browser.py      # TUI UI - remove
   ├── form_*.py (5 files)  # TUI forms - remove
   ├── ui_elements.py       # TUI UI - remove
   └── vibe_dispatch_adapter.py  # Bridge to Vibe (in use)
   ```

   **Distinction**:
   - **Remove**: Interactive REPL, TUI rendering, UI elements
   - **Evaluate**: Command dispatcher (may be used for shell execution)
   - **Keep**: Vibe bridge adapter, command routing logic

2. **Entry Point** (`pyproject.udos.toml`)
   ```toml
   [project.scripts]
   ucli = "core.tui.ucli:main"  # Currently starts interactive TUI
   ```

   **Decision**: Either remove or refactor to CLI-only (no interactive mode)

3. **TUI Dependencies** (prompt_toolkit, rich, etc.)
   - Listed in `pyproject.udos.toml` dependencies
   - Some used by Vibe, some legacy-only

4. **Environment Variables** (`.env.example`)
   ```bash
   UDOS_TUI_CLEAN_STARTUP=1
   UDOS_TUI_STARTUP_EXTRAS=0
   UDOS_TUI_FULL_METERS=0
   UDOS_TUI_INVERT_HEADERS=0
   UDOS_TUI_MAP_LEVEL=1
   UDOS_TUI_FORCE_STATUS=0
   UDOS_TUI_MESSAGE_THEME=<theme>
   UDOS_TUI_LERemove Interactive TUI, Keep Command Infrastructure (Recommended)

**Pros:**
- Clean interactive layer (Vibe-only)
- Preserves command execution infrastructure
- Clear separation: commands (keep) vs TUI (remove)
- Removes ~6000 LOC of UI code

**Cons:**
- Need to carefully identify infrastructure vs UI code
- Some refactoring required

**Actions:**
1. **Remove UI/Rendering Components**:
   - Archive `renderer.py`, `status_bar.py`, `ui_elements.py`
   - Archive `file_browser.py`, `form_*.py`
   - Remove interactive REPL loop from `ucli.py`, `ucode.py`

2. **Keep Command Infrastructure**:
   - Keep `dispatcher.py` (used for shell command execution)
   - Keep `vibComplete UI Removal (Aggressive)

**Remove Everything**:
- All of `core/tui/`
- All TUI-specific code

**Rely on**:
- Vibe CLI bash tool for shell commands: `/bash ucli COMMAND`
- Vibe MCP tools for skill-based routing
- Direct Python API for programmatic access

**Pros:**
- Maximum simplification
- Zero TUI maintenance
- Forces Vibe-first architecture

**Cons:**
- No standalone command execution (always requires Vibe)
- May lose shell scripting flexibility
- Background task management needs different approachf still used by MCP bridge
4. Remove TUI-specific env vars
5. Archive TUI documentation

### Option B: Minimal Preservation

**Keep:**
- `core/tui/vibe_dispatch_adapter.py` (if MCP bridge uses it)
- Critical form handlers (if Vibe uses them)

**Remove:**
- Standalone REPL (`ucli.py`, `ucode.py`)
- TUI rendering (`renderer.py`, `status_bar.py`, `ui_elements.py`)
- Interactive browsers (`file_browser.py`)

**Pros:**
- Keeps shared utilities
- Smaller code footprint
- Clearer separation

**Cons:**
- Partial cleanup, ongoing confusion
- Still need to maintain bridge code

### Option C: Deprecate & Archive (Conservative)

Move everything to `.archive/` but keep accessible for reference during transition period.

**Timeline:**
- 2026-Q1: Deprecate, add warnings
- 2026-Q2: Archive
- 2026-Q3: Remove

---

## Command Execution Pathways

**Key Principle**: Commands are backend services, not TUI features. The interactive TUI is being removed, but all commands remain accessible through multiple execution contexts.

### ✅ Primary: Vibe CLI Interactive
```bash
vibe  # Interactive mode
# User: "show me the map"
# → Vibe routes to ucode_map tool
# → MCP bridge calls core command handler
```

### ✅ Shell Commands (via Vibe bash tool)
```bash
vibe
# User: "/bash ucli MAP"
# → Executes ucode command via Vibe's bash tool
# → Background tasks report progress via status commands
```

### ✅ Background Tasks with Progress Tracking
```bash
# Command runs in background
vibe
# User: "/bash ucli SETUP WIZARD"
# → Starts background installation

# Check progress later
# User: "/bash ucli SETUP CHECK --vibe"
# → Reports installation progress, logs, status
```

### ✅ Direct: Python API (Internal)
```python
from core.services.command_dispatch_service import CommandDispatchService
dispatcher = CommandDispatchService()
result = dispatcher.dispatch("MAP")
```

### ✅ Vibe Skills (High-Level)
```bash
vibe
# User: "install wizard server"
# → Vibe infers skill: workspace.setup
# → Routes to appropriate ucode command
# → Returns progress updates to user
```

### ❌ Legacy: Standalone ucli REPL (to be removed)
```bash
ucli  # Would start standalone interactive TUI - DEPRECATED
```

**Note**: The `ucli` command itself remains as a CLI tool (shell command executor), but the standalone interactive REPL/TUI mode is removed. All interactive workflows go through Vibe CLI.

---

## Dependencies Review

### Core Dependencies (Keep - Used by Vibe)
```toml
python-dotenv>=1.0.0
tzlocal>=4.0
pytz>=2023.3
jsonschema>=4.0.0
PyYAML>=6.0.0
cryptography>=41.0.0
requests>=2.31.0
psutil>=5.9.0
```

### TUI-Specific (Evaluate for Removal)
```toml
prompt_toolkit>=3.0.0  # Used by ucli REPL - CHECK if Vibe uses
rich>=13.0.0           # Used by ucli rendering - CHECK if Vibe uses
```

**Action**: Verify if Vibe or MCP bridge use these. If not, remove.

### Wizard Server (Keep - Still in use)
```toml
fastapi>=0.109.0
uvicorn>=0.27.0
# ... etc
```

---

## Documentation Migration

### Files to Archive

Move to `docs/.archive/tui-legacy-2026-02/`:

1. **Direct TUI References:**
   - `docs/howto/VIBE-UCLI-INTEGRATION-GUIDE.md` - Integration guide for old TUI
   - `docs/dev/core-tui.md` - TUI development guide
   - `docs/guides/TUI-SMART-FIELDS-GUIDE.md` - Form field guide

2. **Partial Updates Needed:**
   - `docs/howto/UCODE-COMMAND-REFERENCE.md` - Remove TUI sections, keep command reference
   - `docs/roadmap.md` - Remove TUI hardening items
   - `.env.example` - Remove UDOS_TUI_* variables

3. **Unclear/Mixed References:**
   - `docs/decisions/TUI-Vibe-Integration.md` - Review, may be current
   - `docs/decisions/vibe-spec-v1-4.md` - Command mapping (should update)
 (interactive)
   - How to run shell commands via Vibe bash tool
   - Background task execution and progress tracking
   - Command examples: `ucli SETUP CHECK --vibe`

2. **Background Task Workflow**
   - Starting background tasks
   - Checking progress: `ucli STATUS TASK_ID`
   - Log streaming and status updates
   - Task cleanup and cancellation

3. **Multi-Context Command Design**
   - Shell execution (direct CLI)
   - Vibe bash tool invocation
   - Vibe skill routing
   - Progress reporting across contexts

4. **Vibe Tool Development**
   - How to add new uDOS commands as Vibe tools
   - MCP server configuration
   - Testing workflow
   - Async/background task integration
   - Update installation to Vibe-only
   - Remove ucli commands

3. **docs/INSTALLATION.md**
   - Already uses vibe-cli (looks good)

4. **docs/roadmap.md**
   - ✅ Already says "Full vibe-cli integration with uCODE TUI complete"
   - ❌ Still has "TUI Parity and Advanced I/O Hardening" section (line 253)
   - ❌ Still has "uCLI map layer rendering extension" (line 285)
   - ❌ Still has "Add CI gate for TUI parity" (line 279)

### New Documentation Needed

1. **Command Execution Guide**
   - How to run uDOS commands via Vibe
   - MCP integration overview
   - Tool discovery and registration

2. **Vibe Tool Development**
   - How to add new uDOS commands as Vibe tools
   - MCP server configuration
   - Testing workflow

---

## Roadmap Updates

### Remove/Archive (Obsolete):

From [docs/roadmap.md](../roadmap.md):rendering
- [ ] Identify command infrastructure vs UI code separation
- [ ] Confirm all commands work via:
  - [ ] Vibe skills (interactive)
  - [ ] Vibe bash tool (`/bash ucli COMMAND`)
  - [ ] Shell (direct execution for background tasks)
- [ ] Map background task progress tracking mechanism
- [ ] Document `ucli SETUP CHECK --vibe` patterned I/O Hardening (Active)"
```markdown
### P0 -- TUI Parity and Advanced I/O Hardening (Active)

- [x] Single-writer stdout lock deployed across prompt/menu/renderer/uCLI interactive paths.
- [ ] **Remove UI Components**:
  - [ ] Archive `renderer.py`, `status_bar.py`, `ui_elements.py`
  - [ ] Archive `file_browser.py`, form handlers
  - [ ] Remove interactive REPL loop code
- [ ] **Preserve Command Infrastructure**:
  - [ ] Keep command dispatcher (shell execution)
  - [ ] Keep background task manager
  - [ ] Keep progress tracking
  - [ ] Keep Vibe bridge adapter
- [ ] **Refactor Entry Points**:
  - [ ] Convert `ucli` to CLI-only (no interactive mode)
  - [ ] Add: `ucli COMMAND --background`
  - [ ] Add: `ucli STATUS TASK_ID`
  - [ ] Add: `ucli LOGS TASK_ID --follow`
- [ ] Update `.env.example` - remove UDOS_TUI_* UI variables
- [ ] Clean up UI dependencies (prompt_toolkit if not used by commands)sion:
  - [ ] Add layered map renderer contract in uCLI
```

**Rationale**: No longer maintaining standalone ucli TUI.

**Line 13**: "Core hardening, gameplay lenses, TUI genres..."
- Update: "Core hardening, gameplay lenses" (remove TUI genres)

**Line 33**: "Full vibe-cli integration with uCODE TUI complete."
- Update: "Full vibe-cli integration complete. Standalone uCODE TUI deprecated."

### Keep (Still Relevant):

- Vibe protocol implementation phases (complete)
- MCP integration (complete)
- Backend service implementation
- Command contract enforcement

---

## Implementation Plan

### Phase 1: Assessment & Documentation (Week 1)
- [x] Audit codebase for TUI references
- [x] Identify files to archive
- [ ] Verify MCP bridge doesn't depend on legacy TUI code
- [ ] Check if `vibe_dispatch_adapter.py` is still needed
- [ ] Confirm all commands work via Vibe tools

### Phase 2: Code Cleanup (Week 2)
- [ ] Move `core/tui/` → `core/.archive/tui-legacy/` (except bridge if needed)
- [ ] Remove `ucli` entryinteractive "ucli REPL" in user-facing docs
- [ ] All uDOS commands executable via:
  - [ ] Vibe CLI interactive (skills/tools)
  - [ ] Vibe bash tool (`/bash ucli COMMAND`)
  - [ ] Shell (for background tasks and scripts)
- [ ] Background task workflow documented and tested:
  - [ ] Start: `ucli SETUP WIZARD --background`
  - [ ] Check: `ucli SETUP CHECK --vibe`
  - [ ] Status: `ucli STATUS TASK_ID`
- [ ] MCP bridge tests passing (100%)
- [ ] Installer smoke tests passing (39/39)
- [ ] Reduced UI codebase size (~6000 LOC removed)
- [ ] Command infrastructure preserved and documented
- [ ] Clear documentation of multi-context command execution
- [ ] Archive TUI-specific guides
- [ ] Update README.md, QUICK-START.md
- [ ] Update roadmap.md - remove TUI hardening tasks
- [ ] Create new "Command Execution via Vibe" guide
- [ ] Update CHANGELOG.md with deprecation notice

### Phase 4: Testing & Validation (Week 3)
- [ ] Verify all Vibe tools still work
- [ ] Test MCP bridge functionality
- [ ] Run smoke tests from installer
- [ ] Update test suites to remove TUI tests
- [Separate command infrastructure from UI code:
   - [ ] Identify dispatcher dependencies
   - [ ] Map background task manager
   - [ ] Document progress tracking mechanism
3. Test multi-context command execution:
   - [ ] Vibe interactive: "install wizard"
   - [ ] Vibe bash: `/bash ucli MAP`
   - [ ] Shell: `ucli SETUP WIZARD --background`
   - [ ] Progress check: `ucli SETUP CHECK --vibe`

**Short-term (This Sprint):**
4. Remove UI components, preserve command infrastructure
5. Refactor `ucli` entry point to CLI-only:
   - [ ] Support: `ucli COMMAND ARG`
   - [ ] Support: `ucli COMMAND --background`
   - [ ] Support: `ucli STATUS TASK_ID`
6. Update documentation (README, QUICK-START, roadmap)
7. Document background task workflow
8. Run full test suite

**Long-term (Next Release):**
9. Create comprehensive multi-context command guide
10. Document background task patterns
11. Create Vibe tool development guide
12. Document MCP architecture for contributors
13. Add CI gates for multi-context command
- Documentation updates
- Environment variable cleanup
- Roadmap updates

### Medium Risk
- Removing TUI code (verify no hidden dependencies)
- Dependency cleanup (ensure Vibe doesn't use prompt_toolkit/rich)

### High Risk
- MCP bridge changes (if vibe_dispatch_adapter.py is modified)
- Breaking existing workflows (verify all commands accessible via Vibe)

---

## Success Criteria

- [ ] Zero references to standalone "ucli" in user-facing docs
- [ ] All uDOS commands executable via Vibe CLI
- [ ] MCP bridge tests passing (100%)
- [ ] Installer smoke tests passing (39/39)
- [ ] Reduced codebase size (~8000 LOC removed)
- [ ] Clear documentation of Vibe-only architecture
- [ ] No regression in command functionality

---

## Rollback Plan

If issues discovered:
1. Restore `core/tui/` from git history
2. Re-add `ucli` entry point
3. Restore env variables
4. Add "Experimental" warning to Vibe-only mode
5. Maintain dual-mode for one more release cycle

---

## Next Steps

**Immediate:**
1. ✅ Confirm MCP bridge doesn't use legacy TUI renderer/REPL code
2. Verify `vibe_dispatch_adapter.py` usage and dependencies
3. Test all commands via Vibe to confirm no missing functionality

**Short-term (This Sprint):**
4. Archive `core/tui/` except essential bridge code
5. Update documentation (README, QUICK-START, roadmap)
6. Remove TUI environment variables
7. Run full test suite

**Long-term (Next Release):**
8. Create comprehensive Vibe tool development guide
9. Document MCP architecture for contributors
10. Add CI gates for Vibe tool coverage

---

## References

- uCODE tools in Vibe: `vibe/core/tools/ucode/`
- MCP server: `wizard/mcp/mcp_server.py`
- Command dispatch: `core/services/command_dispatch_service.py`
- Vibe integration spec: `docs/decisions/vibe-spec-v1-4.md`
- TUI integration (legacy): `docs/howto/VIBE-UCLI-INTEGRATION-GUIDE.md`
- Phase A removal: `vibe/core/tools/ucode/_base.py` (RuntimeError on offline fallback)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-22 | Assess TUI migration | User confirmed Vibe-only architecture |
| TBD | Choose Option A/B/C | Based on MCP bridge dependency analysis |
| TBD | Archive timeline | Based on risk assessment results |

