# Mistral Vibe + uDOS Architecture
## Non-Fork Integration Strategy

This document describes how the repository maintains a clean addon architecture on top of Mistral Vibe, allowing safe local evolution without forking runtime internals.

---

## Core Principle: Addon Model Over Fork

**Never modify vibe/* core files.** Instead:

1. **Extend vibe via its public APIs** (BaseTool, ToolManager, skills)
2. **Keep all uDOS code isolated** in `core/`, `wizard/`, `docs/`
3. **Integration point: `.vibe/config.toml`** (single source of truth)
4. **Custom tools/skills live in vibe/core/tools/ucode/ and vibe/core/skills/ucode/** (outside vibe distribution)

Vibe CLI is installed globally, while this repository provides the local ucode overlay and Wizard integrations.

---

## Repository Structure

```
uDOS-vibe/
├── vibe/                          ← Vibe runtime surface (treated as external interface)
│   ├── cli/
│   ├── core/
│   │   ├── tools/                 ← Vibe's built-in tools
│   │   ├── tools/ucode/           ← OUR Python tool wrappers (Phase A)
│   │   ├── skills/ucode/          ← OUR Markdown skill files (Phase A)
│   │   └── ...vibe core
│   └── ...
│
├── core/                          ← uDOS core (isolated, independent)
│   ├── commands/                  ← SETUP, REPAIR, SEED handlers
│   ├── framework/                 ← seed_installer, templates
│   ├── services/                  ← vault, identity, workspace, wizard, command dispatch
│   ├── tui/                       ← Command infrastructure (dispatcher, vibe bridge)
│   │                              │  Note: command infrastructure only; interactive flow runs through Vibe CLI
│   ├── memory/                    ← RUNTIME (memory/vault, memory/logs) [.gitignored]
│   └── ...rest of uDOS
│
├── wizard/                        ← uDOS web service
│   ├── mcp/                       ← MCP server (Phase B upgrade path)
│   ├── routes/
│   ├── services/
│   ├── security/
│   └── ...
│
├── .vibe/                         ← Vibe configuration (committed)
│   ├── config.toml                ← THE integration point
│   ├── tools/ → symlink           ← vibe/core/tools/ucode/
│   ├── skills/ → symlink          ← vibe/core/skills/ucode/
│   └── ...
│
├── memory/                        ← RUNTIME vault/logs (created at first run) [.gitignored]
│   ├── vault/                     ← User markdown notes (seeded from core/framework/seed/vault/)
│   ├── bank/                      ← Help system, templates, workflows
│   ├── logs/                      ← TUI logs, monitoring data
│   └── ...
│
├── vault/                         ← TEMPLATE structure only (committed)
│   ├── @inbox/, @sandbox/, etc.   ← Directories (no live user content)
│   ├── README.md                  ← Framework docs
│   └── Welcome to Markdown Vault.md
│
├── .env.example                   ← Template (committed)
├── .gitignore                     ← Properly ignores memory/, *.tomb, *.db, etc.
├── pyproject.toml                 ← Vibe + uDOS deps merged
├── pyproject.udos.toml            ← repository-local uDOS config (legacy compatibility, optional)
└── ...
```

---

## User Interface Architecture

### Vibe CLI: Exclusive Interactive Interface

**Interactive workflows**: All handled by Mistral Vibe CLI (`vibe` command)
- Natural language command routing
- AI-powered skill inference
- Rich formatted output
- Progress tracking

**Command execution contexts**:
1. **Vibe interactive**: Skills route to MCP → uDOS commands
2. **Vibe bash tool**: `/bash ucode COMMAND` for shell execution
3. **Shell/scripts**: Direct `ucode COMMAND` for automation/background tasks
4. **Python API**: Internal `CommandDispatchService` for programmatic access

Legacy pre-`vibe-cli` interactive planning docs were composted to:
- `docs/.compost/tui-legacy-2026-02/TUI-MIGRATION-PLAN.md`
- `docs/.compost/tui-legacy-2026-02/VIBE-UCLI-INTEGRATION-GUIDE.md`

---

## Integration Point: `.vibe/config.toml`

The `.vibe/config.toml` file is the **single source of truth** for how vibe discovers and uses uDOS tools and skills.

```toml
# ── Wizard MCP Server ────────────────────────────────────────
[[mcp_servers]]
name      = "wizard"
transport = "stdio"
command   = "venv/bin/python"
args      = ["wizard/mcp/mcp_server.py"]

  [mcp_servers.env]
  PYTHONPATH                     = "."
  WIZARD_MCP_REQUIRE_ADMIN_TOKEN = "0"

# ── Tool paths ───────────────────────────────────────────────
tool_paths = [
    "vibe/core/tools/ucode",
]

# ── Skill paths ──────────────────────────────────────────────
skill_paths = [
    "vibe/core/skills/ucode",
]
```

**When vibe starts:**
1. Reads `.vibe/config.toml` (committed, safe)
2. Auto-discovers tools in `vibe/core/tools/ucode/` via ToolManager
3. Auto-discovers skills in `vibe/core/skills/ucode/` via skill loader
4. Registers MCP server (optional, Phase B)

**vibe never touches core/ directly.** Integration is entirely through config + symlinks.

---

## Three Phases of Integration

### Phase A: Direct Dispatch (Current)

**Tools**: Python BaseTool wrappers in `vibe/core/tools/ucode/*.py`
- Each wraps a uDOS command handler
- Routes through `CommandDispatchService` in-process
- Works offline (no external server needed)
- Backend commands, not UI features

**Skills**: Markdown files in `vibe/core/skills/ucode/*.md`
- Frontmatter-driven AI guidance
- Narrative, multi-step interactions
- Prompt-based, not programmatic

```python
# vibe/core/tools/ucode/_base.py
# Note: Phase A offline dispatch removed in favor of MCP
def _dispatch(command: str, **_: Any) -> dict[str, Any]:
    raise RuntimeError(
        "Phase A offline fallback removed. "
        "Tools must use Vibe MCP server (wizard/mcp/mcp_server.py)."
    )
```

**Current**: All tools use MCP bridge (Phase B).

### Phase B: MCP Server (Current)

**All uDOS tools now use MCP**: Run `wizard/mcp/mcp_server.py` as stdio MCP server.

```toml
# .vibe/config.toml
[[mcp_servers]]
name = "wizard"
transport = "stdio"
command = "uv"
args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]
```

**Flow**:
```
Vibe CLI tool call
    ↓
MCP stdio protocol
    ↓
wizard/mcp/mcp_server.py
    ↓
CommandDispatchService
    ↓
uDOS command handlers (core/services/)
```

**Benefits**:
-Process isolation
- Clean protocol boundary
- Async support
- Progress streaming
- Standard MCP interface

### Phase C: Distributed MCP (Future)

Expose uDOS as a remote MCP server (HTTP, WebSocket). Vibe clients connect remotely.

---

## Vibe Sync Strategy: Local Overlay, No Upstream Remote Requirement

### How to keep this repo aligned safely:

```bash
# 1. Keep global vibe up to date
curl -fsSL https://vibe.mistral.ai/install.sh | sh

# 2. Keep project dependencies aligned
uv sync --extra udos-wizard

# 3. Validate local overlay contract
uv run --project . wizard/mcp/mcp_server.py
vibe
```

**Why this works:**
- ✅ vibe/* never modified → no merge conflicts
- ✅ vibe/core/tools/ucode/ is OUR code → always compatible
- ✅ core/ is isolated → never touched by vibe
- ✅ `.vibe/config.toml` is the contract → changes there are deliberate

### Potential Break Points (Low Risk)

| Change | Impact | Detection |
|--------|--------|-----------|
| `BaseTool.run()` signature changes | Medium | Type checker + tests fail |
| `ToolManager` loader API changes | Low | Tool discovery tests fail |
| `Skill` markdown parser changes | Low | Skill loading tests fail |
| Optional deps removed | Low | `uv sync` fails clearly |

**Mitigation**: Keep ucode additions in addon layers and validate MCP/tool loading after upgrades.

---

## Installation & First Run

### For a new user or developer:

```bash
# 1. Clone (or pull latest)
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS-vibe

# 2. Set up environment (with uDOS)
uv sync --extra udos-wizard
cp .env.example .env       # User edits: MISTRAL_API_KEY, OS_TYPE

# 3. SETUP story (interactive, creates memory/, .env updates, WIZARD_KEY)
uv run ./uDOS.py SETUP     # Runs setup story and seeds runtime state

# 4. Start vibe (reads .vibe/config.toml, discovers tools/skills)
vibe trust                 # Trust current folder (one-time)
vibe                       # Launch interactive agent
```

**What happens inside:**
1. `python uDOS.py` → `from core.tui.ucode import main; main()`
2. SETUP story collects identity, writes `.env`
3. REPAIR --check auto-heals missing directories
4. SeedInstaller seeds `memory/vault/` from `core/framework/seed/vault/`
5. `vibe` reads `.vibe/config.toml`, discovers tools/skills, starts agent

**No separate installer needed.** Self-healing architecture handles bootstrap.

---

## File Ownership & Modification Rules

### ✅ Safe to Modify (Our Addon Code)

```
vibe/core/tools/ucode/*.py         ← Tool implementations
vibe/core/skills/ucode/*.md        ← Skill definitions
core/**/*.py                       ← uDOS core (untouched by vibe)
wizard/**/*.py                     ← Wizard server
.vibe/config.toml                  ← Configuration
.env.example                       ← Environment template
pyproject.toml [ucode-*]           ← uDOS optional deps
docs/**/*.md                       ← Our documentation
```

### ❌ Never Modify (Vibe Upstream)

```
vibe/cli/**              ← CLI entry point (not our code)
vibe/core/tools/base.py  ← BaseTool API (not our code)
vibe/core/skills/base.py ← Skill loader (not our code)
vibe/core/tools/[anything except ucode/] ← Built-in tools
vibe/core/skills/[anything except ucode/] ← Built-in skills
```

**If you need to extend vibe behavior**, create a symlink to `.vibe/tools/` or `.vibe/skills/` pointing to our addon directories.

---

## Testing the Non-Fork Strategy

### Quick validation:

```bash
# 1. Verify no vibe/ files were modified since external runtime
git log --oneline vibe/ | head -1  # Should be from external runtime merge

# 2. Verify tool discovery works
python -c "
from vibe.core.tools.tool_manager import ToolManager
tm = ToolManager()
tools = tm.resolve_local_tools_dir('vibe/core/tools/ucode')
print(f'Discovered {len(tools)} ucode tools')
"

# 3. Verify skill discovery works
python -c "
from vibe.core.skills.skill_manager import SkillManager
sm = SkillManager()
skills = sm.discover_skills('vibe/core/skills/ucode')
print(f'Discovered {len(skills)} ucode skills')
"

# 4. Run full integration test
vibe -p "Use the HEALTH tool"
```

---

## Versioning & Compatibility

### vibe vs uDOS versions

```
pyproject.toml:
  mistralai==1.9.11        # Vibe version pinned
  mcp>=1.14.0              # MCP protocol version (flexible)

pyproject.udos.toml:
  version = "1.4.6"        # uDOS version (legacy, optional)
```

**Policy:**
- Vibe updates come from the official global installer and local validation checks
- uDOS version tracks separately in `version.json`
- Tool API (Phase A) is stable within Vibe major versions
- Phase B (MCP) uses MCP protocol versioning (independent)

---

## Avoiding the Fork

| Temptation | Why It's Bad | Our Answer |
|------------|-------------|-----------|
| "Modify vibe/ to add our feature" | Forces fork → diverges from external runtime | Use `.vibe/config.toml` + symlinks to extend |
| "Keep our own copy of Vibe" | Duplicates code, misses security updates | Keep global Vibe updated via official installer |
| "Patch vibe locally via monkey-patching" | Fragile, breaks on updates | Implement in addon layer (BaseTool subclass) |
| "Commit secrets to git" | Leaks credentials | `.gitignore` `, `.env` example-only, runtime `.env` ignored |

**The cost of a fork:**
- 10-50 commits diverged per quarter
- Manual merges of security fixes
- Upstream improvements never land
- Difficult for contributors to onboard

**Our cost of a clean addon layer:**
- 20-line symlink setup
- `.vibe/config.toml` maintenance (1 file, infrequent changes)
- Upstream merges are clean (git merge, not manual patching)

---

## Summary

**mistral-vibe-base is a clean addon installation of Mistral Vibe, not a fork.**

- Vibe core is untouched
- uDOS tools/skills extend via public APIs
- Integration via `.vibe/config.toml` + symlinks
- Upstream merges are safe and clean
- Phase A (direct dispatch) → Phase B (MCP) upgrade path is transparent

**This architecture scales:**
- Multiple teams can maintain separate addon layers
- Vibe external runtime updates don't break our workflows
- Contributors can easily merge in security patches
- No vendor lock-in or fork divergence
