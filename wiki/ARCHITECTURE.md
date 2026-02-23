# uDOS Architecture

**Version:** v1.4.4+
**Last Updated:** 2026-02-22
**Status:** Active

uDOS is an offline‑first, vault‑based system with Vibe CLI as the exclusive interactive interface, plus optional wizard services and modular extensions.

---

## Overview

```
uDOS/
├── vibe/          # Mistral Vibe CLI (exclusive interactive UI)
├── core/          # Offline runtime + command infrastructure
├── wizard/        # Optional MCP server + web services
├── sonic/         # Bootable USB entry point
├── library/       # Container definitions
├── extensions/    # Transport API contracts
├── docs/          # Architecture + specs
├── wiki/          # Beginner-friendly docs
└── knowledge/     # Static knowledge catalog
```

---

## Vibe CLI (Interactive Interface)
**Location:** `vibe/` (Mistral Vibe upstream)

**Responsibilities**
- Interactive command-line interface
- Natural language skill routing
- AI-powered command inference
- MCP protocol client

**Integration**
- uDOS tools: `vibe/core/tools/ucode/`
- Configuration: `.vibe/config.toml`
- MCP bridge to uDOS commands

---

## Core (Command Infrastructure)
**Location:** `core/`

**Responsibilities**
- Command execution (stdlib Python only, no networking)
- Vault-first file access
- uCODE command surface (55+ commands)
- Background task management
- Progress tracking

**Boundaries**
- ✅ No network dependency
- ✅ Local-only by default
- ✅ Stdlib Python only
- ❌ No cloud services
- ❌ No interactive UI (handled by Vibe)

---

## Wizard (MCP Server + Web Services)
**Location:** `wizard/`

**Responsibilities**
- MCP server (stdio bridge to uDOS commands)
- AI routing (local-first via Ollama, optional cloud)
- Web admin dashboard
- Plugin registry + update routing
- Networking, security, packaging tools

**Boundaries**
- ✅ Stateless (no user data at rest)
- ✅ LAN-first
- ✅ Extended command set (beyond core)
- ❌ No core command logic (delegated to core/)

---

## Sonic (Bootable Entry)
**Location:** `sonic/`

**Responsibilities**
- USB builder
- Bootable entry point
- Media management
- Distribution tooling

---

## Command Execution

uDOS commands execute in multiple contexts:

1. **Vibe CLI interactive**: Natural language → skills → MCP → commands
2. **Vibe bash tool**: `/bash ucode COMMAND` for shell execution
3. **Shell/scripts**: Direct `ucode COMMAND` for automation
4. **Python API**: Internal `CommandDispatchService`

See: [docs/decisions/TUI-Vibe-Integration.md](../docs/decisions/TUI-Vibe-Integration.md)

---

## Extensions + Containers
**Location:** `library/`, `extensions/`

**Responsibilities**
- Container definitions (library)
- API contracts (extensions)

---

## Versioning
- Command infrastructure is preserved from previous releases, now accessible via Vibe CLI and shell.
- Submodules can ship on their own cadence.

---

## Related Docs
- `docs/README.md`
- `docs/roadmap.md`
- `docs/specs/wiki_spec_obsidian.md`
