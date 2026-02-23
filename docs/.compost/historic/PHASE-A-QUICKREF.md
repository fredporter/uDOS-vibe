# Phase A Development Quick Reference
## Building uDOS Tools & Skills for Vibe

---

## Quick Start

You are about to scaffold Phase A:
- **5 tool modules** in `vibe/core/tools/ucode/` (40+ commands)
- **5 skill files** in `vibe/core/skills/ucode/` (narrative interactions)

This document is your coordinate system.

---

## Project Map

```
mistral-vibe-base/
├── vibe/core/tools/ucode/              ← You're building here
│   ├── __init__.py                     # Tool registry
│   ├── _base.py                        # Shared UcodeBaseTool pattern
│   ├── spatial.py                      # MAP, GRID, ANCHOR, GOTO, FIND
│   ├── system.py                       # HEALTH, VERIFY, REPAIR, UID, TOKEN, VIEWPORT
│   ├── data.py                         # BINDER, SAVE, LOAD, SEED, MIGRATE, CONFIG
│   ├── workspace.py                    # WORKSPACE, SCHEDULER, SCRIPT, USER
│   └── content.py                      # DRAW, SONIC, MUSIC, EMPIRE, DESTROY, UNDO
│
├── vibe/core/skills/ucode/             ← And here
│   ├── ucode-help/SKILL.md             # Help + natural language lookup
│   ├── ucode-setup/SKILL.md            # Multi-step onboarding
│   ├── ucode-story/SKILL.md            # Run/read narrative content
│   ├── ucode-logs/SKILL.md             # Diagnostic + explanations
│   └── ucode-dev/SKILL.md              # Dev mode + explanations
│
├── core/tui/
│   ├── dispatcher.py                   ← CommandDispatcher (THE router)
│   └── ucode.py                        ← Handler definitions
│
├── docs/
│   ├── ARCHITECTURE.md                 ← Non-fork strategy
│   ├── INTEGRATION-READINESS.md        ← Project readiness
│   ├── AUDIT-RESOLUTION.md             ← What was fixed
│   ├── PHASE-A-ROADMAP.md              ← (You'll create this)
│   └── ...
│
└── .vibe/
    ├── config.toml                     ← Integration point (already set up)
    ├── tools/ → symlink                ← Auto-discovered
    └── skills/ → symlink               ← Auto-discovered
```

---

## The Pattern: One Tool, One Command

### Before (how uDOS works now)

```bash
uDOS.py HEALTH --check db
# → Dispatcher routes to HealthHandler → Returns dict
```

### After (what you're building)

```python
# vibe/core/tools/ucode/system.py

class UcodeHealth(BaseTool[HealthArgs, UcodeResult, ...]):
    """Run a uDOS health check."""

    async def run(self, args: HealthArgs, ctx) -> AsyncGenerator[...]:
        cmd = f"HEALTH {args.check}".strip() if args.check else "HEALTH"
        result = _dispatch(cmd)  # ← Calls dispatcher
        yield UcodeResult(**result)
```

When user asks Mistral: *"Check health"*
→ Mistral calls `ucode_health(check="")`
→ Your `run()` method executes
→ Dispatcher returns result
→ Mistral gets the output

---

## Core Concepts

### 1. **_dispatch(command: str) → dict**

All commands route through `CommandDispatcher().dispatch(cmd)`.

```python
from core.tui.dispatcher import CommandDispatcher

result = CommandDispatcher().dispatch("HEALTH --check db")
# Returns: {"status": "ok", "output": "...", "data": {...}}
```

Your tool just wraps this call with typing + streaming.

### 2. **BaseTool Pattern**

```python
from vibe.core.tools.base import BaseTool, BaseToolConfig, BaseToolState, InvokeContext
from pydantic import BaseModel, Field

class HealthArgs(BaseModel):
    check: str = Field(default="", description="Subsystem to check")

class UcodeResult(BaseModel):
    status: str
    message: str
    data: dict = Field(default_factory=dict)

class UcodeHealth(BaseTool[HealthArgs, UcodeResult, BaseToolConfig, BaseToolState]):
    description = "Run a uDOS health check"

    async def run(self, args: HealthArgs, ctx: InvokeContext | None = None):
        cmd = f"HEALTH {args.check}".strip() if args.check else "HEALTH"
        yield UcodeResult(**_dispatch(cmd))
```

**Four types you need:**
1. `Args` — Pydantic model of function parameters
2. `Result` — Pydantic model of return type
3. `Config` — Tool config (usually `BaseToolConfig`)
4. `State` — Tool state (usually `BaseToolState`)

### 3. **Streaming**

All tools are async generators. Even if there's no streaming:

```python
# ✅ Correct
async def run(self, args, ctx):
    yield Result(...)

# ❌ Wrong (won't be discovered)
def run(self, args, ctx):
    return Result(...)
```

### 4. **Phase A → Phase B Upgrade**

Write _dispatch() to be swappable:

```python
def _dispatch(command: str) -> dict:
    # Phase A: Direct
    from core.tui.dispatcher import CommandDispatcher
    return CommandDispatcher().dispatch(command)

# Phase B: Just replace this with:
def _dispatch(command: str) -> dict:
    return mcp_client.call_tool("ucode_dispatch", {"command": command})
```

Schema never changes. Mistral sees no difference.

---

## File Structure Template

### `_base.py` — Shared Helpers

```python
"""
Shared uDOS tool adapter layer.

Phase A: Commands dispatch directly via CommandDispatcher.
Phase B: Swap _dispatch() body to call MCP server instead.
"""

from core.tui.dispatcher import CommandDispatcher

def _dispatch(command: str) -> dict:
    """Route command through dispatcher."""
    try:
        return CommandDispatcher().dispatch(command)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _normalize(result: dict) -> dict:
    """Normalize dispatcher output to tool result format."""
    # Ensure all results have status, message, data keys
    return {
        "status": result.get("status", "error"),
        "message": result.get("message", "No output"),
        "data": result.get("data", {}),
    }
```

### `spatial.py` — Example Module

```python
"""MAP, GRID, ANCHOR, GOTO, FIND commands."""
from pydantic import BaseModel, Field
from vibe.core.tools.base import BaseTool, InvokeContext
from vibe.core.types import ToolStreamEvent
from ._base import _dispatch, _normalize

class FindArgs(BaseModel):
    query: str = Field(description="Search term or location name")
    filter_type: str = Field(default="", description="Optional filter")

class UcodeResult(BaseModel):
    status: str
    message: str
    data: dict = Field(default_factory=dict)

class UcodeFind(BaseTool):
    description = "Search for locations, items, or NPCs"

    async def run(self, args: FindArgs, ctx: InvokeContext | None = None):
        cmd = f"FIND {args.query}"
        if args.filter_type:
            cmd += f" --filter {args.filter_type}"
        result = _dispatch(cmd)
        yield UcodeResult(**_normalize(result))

# Repeat for MAP, GRID, ANCHOR (3-4 tools per file)
```

### `SKILL.md` — Skill Template

```markdown
---
name: ucode-help
title: uDOS Help & Documentation
description: Natural language help lookup and command guidance
prompt: |
  The user wants to learn about uDOS commands or get help.
  Guide them with clear examples and suggest the right command.
  Be conversational and explain what each command does.
invocation:
  - "help me with"
  - "how do I"
  - "what does"
  - "explain"
---

# uDOS Help

This skill helps users navigate the uDOS command surface.

## Key Topics

- **System Health** - HEALTH, REPAIR, VERIFY
- **Identity** - UID, TOKEN, USER
- **Navigation** - MAP, GRID, FIND, GOTO
- **Data** - BINDER, SAVE, LOAD, MIGRATE
- **Stories** - STORY, RUN, READ

Ask the user what they need help with, then guide them to the right command.
```

---

## Command Mapping Checklist

### Tool Commands (Programmatic)

```
spatial.py:
  □ MAP      (show spatial map)
  □ GRID     (query grid)
  □ ANCHOR   (set anchor point)
  □ GOTO     (navigate to)
  □ FIND     (search)

system.py:
  □ HEALTH   (check subsystems)
  □ VERIFY   (verify installation)
  □ REPAIR   (self-heal)
  □ UID      (generate user ID)
  □ TOKEN    (generate token)
  □ VIEWPORT (get terminal size)

data.py:
  □ BINDER   (manage data store)
  □ SAVE     (persist state)
  □ LOAD     (restore state)
  □ SEED     (bootstrap data)
  □ MIGRATE  (data migration)
  □ CONFIG   (read/write config)

workspace.py:
  □ WORKSPACE (switch workspace)
  □ USER      (user profile)
  □ SCHEDULER (task scheduling)
  □ SCRIPT    (run named script)

content.py:
  □ DRAW      (ASCII rendering)
  □ SONIC     (audio playback)
  □ MUSIC     (music selection)
  □ EMPIRE    (entity query)
  □ DESTROY   (destructive action)
  □ UNDO      (rollback)
```

### Skill Commands (Narrative)

```
ucode-help:
  □ HELP     (interactive help)

ucode-setup:
  □ SETUP    (onboarding story)

ucode-story:
  □ STORY    (run narrative)
  □ RUN      (execute story)
  □ READ     (read content)

ucode-logs:
  □ LOGS     (diagnostic logs)

ucode-dev:
  □ DEV      (dev mode toggle)
  □ GHOST    (ghost mode policy)
```

---

## First Tool: Step-by-Step

### 1. Create `vibe/core/tools/ucode/_base.py`

```python
"""Shared uDOS tool dispatcher."""
from core.tui.dispatcher import CommandDispatcher

def _dispatch(cmd: str) -> dict:
    return CommandDispatcher().dispatch(cmd)

def _normalize(result: dict) -> dict:
    return {
        "status": result.get("status", "error"),
        "message": result.get("message", ""),
        "data": result.get("data", {}),
    }
```

### 2. Create `vibe/core/tools/ucode/system.py`

```python
"""HEALTH, VERIFY, REPAIR, UID, TOKEN, VIEWPORT."""
from pydantic import BaseModel, Field
from vibe.core.tools.base import BaseTool, InvokeContext
from vibe.core.types import ToolStreamEvent
from ._base import _dispatch, _normalize

class UcodeResult(BaseModel):
    status: str
    message: str
    data: dict = Field(default_factory=dict)

class HealthArgs(BaseModel):
    check: str = Field(default="", description="Subsystem: db, wizard, vault, memory, etc.")

class UcodeHealth(BaseTool):
    """Run health check on uDOS subsystems."""

    async def run(self, args: HealthArgs, ctx: InvokeContext | None = None):
        cmd = f"HEALTH {args.check}".strip() if args.check else "HEALTH"
        yield UcodeResult(**_normalize(_dispatch(cmd)))

# Repeat for VERIFY, REPAIR, UID, TOKEN, VIEWPORT
```

### 3. Test Discovery

```bash
python -c "
from vibe.core.tools.tool_manager import ToolManager
tm = ToolManager()
tools = tm.resolve_local_tools_dir('vibe/core/tools/ucode')
print(f'Found {len(tools)} tools: {list(tools.keys())}')
"
```

### 4. Test with vibe

```bash
vibe -p "Run a health check" --enabled-tools "ucode*"
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Non-async `run()` method | Use `async def run(...):` and `yield` |
| Returning instead of yielding | Use generators: `yield result` not `return` |
| Missing Pydantic models | All args/results must be BaseModel subclasses |
| Forgetting tool discovery | Tools must inherit from BaseTool and define `description` |
| Typo in command | Check dispatcher: `CommandDispatcher().dispatch("HEALTH")` |
| No tool in `.vibe/tools/` symlink | Symlink should point to `vibe/core/tools/ucode/` |

---

## How Mistral Discovers & Calls Your Tool

```
1. Vibe startup reads .vibe/config.toml
2. ToolManager.resolve_local_tools_dir() scans vibe/core/tools/ucode/
3. Finds all classes inheriting from BaseTool
4. Extracts JSON schema from args models
5. Sends to Mistral API
6. User asks: "Check the system health"
7. Mistral calls: ucode_health(check="")
8. Your run() method executes
9. Returns result to Mistral
10. Mistral responds to user
```

---

## Testing Locally

```bash
# 1. Install editable + udos deps
pip install -e .[udos-wizard]

# 2. Run interactive vibe
vibe

# 3. In vibe shell, ask:
"What tools do you have available?"

# 4. Or use programmatic mode:
vibe -p "Run a health check" --enabled-tools "ucode_health"
```

---

## Questions?

Refer to:
- **`docs/ARCHITECTURE.md`** — how addon layer works
- **`docs/INTEGRATION-READINESS.md`** — project prerequisites
- **`docs/AUDIT-RESOLUTION.md`** — what was fixed and why
- **`vibe/core/tools/base.py`** — BaseTool API (read the docstrings)
- **`core/tui/dispatcher.py`** — CommandDispatcher interface

---

## After Phase A

Once all 40+ tools + 5 skills are scaffolded:

1. **Create `docs/PHASE-A-ROADMAP.md`** — implementation checklist
2. **Update `docs/ARCHITECTURE.md` Phase B section** with MCP upgrade details
3. **Run integration tests:** `vibe -p "Use 5 different uDOS tools"`
4. **Document:** Which commands → tool vs. skill

Then: Phase B (swap dispatcher to MCP server).

---

**You've got this. Start with the template, repeat for 5 modules, and ship it.** 🚀
