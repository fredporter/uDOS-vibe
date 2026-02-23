# uDOS v1.4.5 +Vibe

```
████████████████████████████████████████████████████████████
██                                                        ██
██   ██████████████████████████████████████████████████   ██
██   ██  ████  ███      ███      ███       ███       ██   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██      ███   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██
██   ███      ████      ███      ███       ███       ██   ██
██   ██████████████████████████████████████████████████   ██
██   ███████████████    ███████████    ████████████████   ██
██   █████████████████  uDOS v1.4.5  ██████████████████   ██
██   ██████████████████████████████████████████████████   ██
██                                                        ██
████████████████████████████████████████████████████████████
```

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

</div>

## What is This?

**uDOS v1.4.5 +Vibe** is an integrated development environment combining:

- **vibe-cli runtime** — Open-source CLI coding assistant with tool execution and subagents
- **uDOS** — Offline-first OS layer for vault workflows, knowledge systems, and portable tooling
- **Wizard** — LAN gateway for extensions, AI routing, and sync

This repository brings together uDOS's extensive command suite (50+ tools) and knowledge system with vibe-cli agent capabilities, without forking Vibe.

### Key Differences from Stock Vibe

| Feature | Stock Vibe | uDOS v1.4.5 +Vibe |
|---------|-----------|------------|
| Installation | Global `vibe` via official installer | Clone repo + `uv venv venv` + `uv sync --extra udos-wizard` |
| Commands | Read/write/bash/git tools | uDOS suite (50+) + Vibe tools |
| Workspace | Project folder | Project + vault + memory + Obsidian |
| Knowledge | Code only | Markdown vault (offline) |
| Extensibility | Skills/MCP | Skills + uDOS Wizard server |
| Setup | Interactive key entry | Auto-generates identity + keys |

> [!WARNING]
> vibe-cli works on Windows, but we officially support and target UNIX environments.

---

## Quick Start

### Prerequisites
- Python 3.12+
- Git
- macOS or Linux (Ubuntu/Alpine recommended)

### Installation

**Option 1: Automated installer (recommended)**

macOS:
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS-vibe

# Run installer (double-click in Finder, or from terminal)
./bin/install-udos-vibe.sh
```

Linux:
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS-vibe

# Run installer
./bin/install-udos-vibe.sh
```

The installer automatically handles:
- ✓ uv package manager installation
- ✓ Environment configuration (.env)
- ✓ Vibe CLI installation
- ✓ Vault structure setup
- ✓ Optional components (micro, Obsidian, Ollama)

**Option 2: Manual installation**

```bash
# Clone and navigate
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS-vibe

# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install uDOS v1.4.5 +Vibe
uv sync --extra udos-wizard

# Copy and configure .env
cp .env.example .env
# Edit `.env` with your provider key settings

# Run setup story
uv run ./uDOS.py SETUP
```

📚 **Full installation guide**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

### First Commands

After installation:

```bash
# Start vibe CLI
vibe

# Or with explicit repo context
cd /path/to/uDOS-vibe && vibe
```

Inside vibe:
```
SETUP          # Complete user configuration
STATUS         # Check system health
HELP           # List available commands
WIZARD start   # Launch web server (optional)
```

**Example flow:**
```
> vibe
Welcome to vibe-cli + uDOS

You: Read the file @core/commands/help.py and explain what it does
🤖: [reads file, explains using agent]

You: Create a new uDOS skill for markdown validation
🤖: [scaffolds skill in vibe/core/skills/ucode/]

You: /list-skills
🤖: Available skills: code-review, markdown-*
```

## Project Structure

```
uDOS-vibe/
├── vibe/                          # vibe-cli runtime (read-only base)
│   ├── cli/                       # Entry point
│   ├── core/
│   │   ├── tools/                 # Built-in tools
│   │   │   └── ucode/             # uDOS tools (addon)
│   │   └── skills/                # Built-in skills
│   │       └── ucode/             # uDOS skills (addon)
│   └── ...vibe/
│
├── core/                          # uDOS core (runtime, framework)
│   ├── commands/                  # Command handlers (50+)
│   ├── framework/                 # Service framework
│   ├── memory/                    # In-memory data structures
│   ├── parsers/                   # Config/spec parsing
│   └── tests/
│
├── wizard/                        # Wizard API gateway
│   ├── mcp_server.py              # MCP interface
│   ├── services/                  # Web/routing services
│   └── tests/
│
├── docs/                          # Development documentation
│   ├── ARCHITECTURE.md            # Addon model, non-fork strategy
│   ├── INTEGRATION-READINESS.md   # Audit results
│   ├── roadmap.md                 # Active milestone and execution plan
│   ├── specs/                     # Format/interface specs
│   ├── howto/                     # Procedures and guides
│   └── decisions/                 # ADRs and design decisions
│
├── tests/                         # Test suite
├── ext/                           # Extensions / plugins
├── memory/                        # Runtime state (git-ignored)
├── vault/                         # Knowledge vault (git-template)
├── wiki/                          # User documentation
│
├── .vibe/config.toml              # Vibe integration config
├── .env.example                   # Environment template
├── pyproject.toml                 # Root deps (Vibe + uDOS)
└── uDOS.py                        # Command dispatcher
```

### Key Files

**`.vibe/config.toml`**
- Integration point for Vibe
- Declares uDOS tool/skill paths
- MCP server configs
- Auto-discovered on startup

**`pyproject.toml`**
- Project metadata
- Vibe + uDOS dependencies
- Optional groups: `[udos]`, `[udos-wizard]`, `[udos-full]`

**`core/commands/`**
- 50+ command implementations
- CommandDispatcher router
- Test fixtures

**`vibe/core/tools/ucode/` & `vibe/core/skills/ucode/`**
- Addon modules managed by this repo overlay
- Custom tools/skills for uDOS
- Safely coexist with Vibe built-ins

---

## Comprehensive Documentation

Start here:
- **New to the project?** → [Getting Started](docs/dev/GETTING-STARTED.md)
- **Architecture & design** → [Architecture Guide](docs/ARCHITECTURE.md)
- **Integration strategy** → [Integration Readiness](docs/INTEGRATION-READINESS.md)
- **Current execution plan** → [Roadmap](docs/roadmap.md)

By category:
- **Development** — [docs/dev/](docs/dev/) — Setup, building, testing
- **Design** — [docs/decisions/](docs/decisions/) — ADRs, rationale
- **Specs** — [docs/specs/](docs/specs/) — Formats, schemas, contracts
- **Procedures** — [docs/howto/](docs/howto/) — Step-by-step guides
- **User Guide** — [wiki/](wiki/Home.md) — End-user documentation

### Documentation Index

- `docs/ARCHITECTURE.md` — How uDOS+Vibe integration works (non-fork model)
- `docs/AUDIT-RESOLUTION.md` — Pre-Phase-A readiness audit results
- `docs/INTEGRATION-READINESS.md` — Project prerequisites and validation
- `docs/PHASE-A-QUICKREF.md` — Developer quick reference for building tools
- `docs/roadmap.md` — Active milestone and release readiness checklist
- `docs/specs/` — Format specifications and contracts
- `docs/decisions/` — Architecture decision records
- `wiki/Home.md` — User guides and getting-started docs

---

## Installation & Setup

### System Requirements

- **Python**: 3.12+ (required)
- **OS**: macOS, Linux, Windows (officially supported on UNIX)
- **Terminal**: Modern emulator recommended (WezTerm, Alacritty, Ghostty, Kitty)

### Installation Methods

#### 1. From Source (Recommended)

```bash
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS-vibe

# Install with uv (recommended)
uv sync --extra udos-wizard
```

#### 2. Quick Dev Setup

```bash
# Copy the workspace config
cp vibe-dev.code-workspace uDOS-vibe.code-workspace

# Open in VS Code
code uDOS-vibe.code-workspace

# Terminal will auto-activate venv and set uDOS env vars
```

### Configuration

On first run, Vibe will prompt for your AI provider API key. It is securely saved to `~/.vibe/.env`.

Alternatively, configure via environment:
```bash
export AI_API_KEY="your-key-here"
```

Or manually create `~/.vibe/.env`:
```ini
AI_API_KEY=your-key-here
AI_API_BASE_URL=https://your-provider.example/v1
```

### Environment Setup

Optional environment variables (see `.env.example`):

```bash
# uDOS settings
UDOS_ROOT=/path/to/uDOS-vibe
UDOS_MEMORY=/path/to/memory
UDOS_VAULT=/path/to/vault

# Wizard server
UDOS_WIZARD_PORT=8000
UDOS_WIZARD_HOST=0.0.0.0
UDOS_WIZARD_KEY="auto-generated-on-setup"

# AI provider API
AI_API_KEY="your-api-key"
```

### Minimum Spec (vibe-cli + uCode Addon)

| Component | Requirement |
|---------|-------------|
| OS | Linux/macOS/Windows 10+ (x86/ARM) |
| CPU | 2 cores (x86/ARM) |
| RAM | 4 GB |
| Storage | 5 GB free (SSD recommended) |
| Network | Optional (online/offline pathways supported) |
| Dependencies | Python 3.8+, vibe-cli, uCode addon |

Operational pathways:
- `With network`: `UCODE` + cloud provider fallback + full command/docs surface.
- `Without network`: `UCODE` + local demo/docs/system-introspection fallback.

See full brief: [`docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md`](docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md).

## Features

### Vibe Features

- **Interactive Chat**: A conversational AI agent that understands your requests
- **Powerful Tools**: Read/write/patch files, execute shell commands, search code, manage todos
- **Project-Aware**: Scans file structure and Git status for context
- **Multiple Agents**: Default, plan, accept-edits, auto-approve profiles
- **Subagents**: Delegate work for parallel processing
- **Skills System**: Extend with custom skills and slash commands
- **MCP Support**: Model Context Protocol servers for additional tools
- **Highly Configurable**: Customize via `~/.vibe/config.toml`

### uDOS Features

- **50+ Commands**: Extensive CLI command suite
- **Vault-Based**: Offline Obsidian-compatible knowledge system
- **Auto-Setup**: Identity + API key auto-generation
- **Self-Healing**: SETUP, REPAIR, SEED commands
- **Wizard Server**: LAN gateway and extension routing
- **Non-Fork**: Addon architecture integrates with Vibe without divergence

---

## Usage

### Interactive Mode

```bash
# Start Vibe
vibe

# Reference files with @
> Read the file @src/main.py

# Use shell commands (prefix with !)
> !ls -la src/

# Create todo items
> Add item to todo: "Refactor authentication"

# Delegate to subagents
> task(task="Explore the codebase", agent="explore")
```

### Non-Interactive / Scripting

```bash
# Single prompt
vibe --prompt "Refactor the main function"

# With specific tools
vibe --enabled-tools "bash*,read_file" --prompt "List files in src/"

# With cost limit
vibe --max-price 2.0 --prompt "Analyze security"

# Output as JSON
vibe --output json --prompt "Check structure"
```

### Command Reference

**Core commands** (handled by uDOS CommandDispatcher):
- `STATUS` — Show system status
- `SETUP` — Initialize identity + keys
- `REPAIR` — Check/fix configuration
- `HELP` — Get command help
- `WIZARD start` — Launch Wizard server

See [docs/howto/UCODE-COMMAND-REFERENCE.md](docs/howto/UCODE-COMMAND-REFERENCE.md) for complete command list.

### Keyboard Shortcuts

- **`Ctrl+J` / `Shift+Enter`** — Multi-line input
- **`Ctrl+G`** — Edit input in external editor
- **`Ctrl+O`** — Toggle tool output
- **`Ctrl+T`** — Toggle todo list
- **`Shift+Tab`** — Toggle auto-approve
- **`/`** — Slash commands
- **`@`** — File path autocompletion

---

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=core --cov=wizard

# Specific test
uv run pytest tests/core/test_commands.py::test_help_handler
```

### Running Linters

```bash
# Format code
uv run ruff format core/ wizard/ tests/

# Check types
uv run pyright core/ wizard/

# Lint
uv run ruff check --fix core/ wizard/
```

### Building Extensions

Tools and Skills are scaffolded in:
- `vibe/core/tools/ucode/*.py` — Tool implementations
- `vibe/core/skills/ucode/*.md` — Skill definitions

See [docs/PHASE-A-QUICKREF.md](docs/PHASE-A-QUICKREF.md) for scaffolding templates.

### Debugging

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=debug
vibe --prompt "test"

# Attach debugger
uv run debugpy -- bin/vibe SETUP
```

---

## Contributing

We welcome contributions! Please see:

- [CONTRIBUTING.md](CONTRIBUTING.md) — Guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community standards
- [docs/decisions/](docs/decisions/) — Design rationale
- [AGENTS.md](AGENTS.md) — Development agents & patterns

---

## Architecture & Design

### Non-Fork Integration Model

uDOS integrates with Vibe *without* forking:

- **Vibe core** (`vibe/*`): treated as external runtime surface; local extensions stay isolated
- **Addon code**: Lives in `vibe/core/tools/ucode/` and `vibe/core/skills/ucode/`
- **Integration**: Declared in `.vibe/config.toml` (committed, under our control)
- **Isolation**: All uDOS logic lives in `core/`, `wizard/`, `tests/`

When Vibe releases an update, this repo remains an overlay for ucode tools/skills and Wizard integration while preserving local command contracts.

### Key Components

**CommandDispatcher** — Router for 50+ uDOS commands
**Wizard** — MCP server + LAN gateway
**ToolManager/SkillManager** — Vibe's tool/skill discovery system
**Framework** — Service layer, memory, parsers

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for comprehensive design guide.

---

## Troubleshooting

**Vibe not finding uDOS tools?**
```bash
# Check tool discovery
uv run python -c "from vibe.core.tools.tool_manager import ToolManager; print(ToolManager().resolve_local_tools_dir('vibe/core/tools/ucode'))"

# Verify config
cat .vibe/config.toml
```

**AI provider API errors?**
```bash
# Check API key
echo $AI_API_KEY

# Test connectivity
vibe --prompt "What version are you?"
```

**Python venv issues?**
```bash
# Reinstall venv
rm -rf venv
uv sync --extra udos-wizard
```

See [docs/troubleshooting/](docs/troubleshooting/) for more.

---

## Resources

- **uDOS v1.4.5 +Vibe** — https://github.com/fredporter/uDOS-vibe
- **MCP Spec** — https://modelcontextprotocol.io
- **Credits** — [wiki/credits.md](wiki/credits.md)
- **Agent Skills** — https://agentskills.io

---

## License

This project integrates vibe-cli runtime components and uDOS (Apache 2.0).

All code is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

## Data & Privacy

Vibe can send code and conversations to your configured AI provider endpoint.
- Review your provider's privacy policy and data terms.
- Disable telemetry: `enable_telemetry = false` in `~/.vibe/config.toml`

uDOS stores runtime data locally in `memory/` (git-ignored).

---

<div align="center">

**Questions?** Open an issue or visit [wiki/Home.md](wiki/Home.md)

Made with ❤️ for developers who want AI + local knowledge

</div>
