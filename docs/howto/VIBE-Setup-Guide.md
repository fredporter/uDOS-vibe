# Vibe Setup Guide (uDOS Overlay)

This repository runs as an overlay on top of globally installed `vibe`.
Do not clone/install a separate local Vibe source tree inside this repo.

## Target Model

- Global Vibe CLI install via official installer
- Single Python environment in repo root: `venv/`
- Project-local Vibe wiring in `.vibe/config.toml`
- ucode command-set delivered through repo-local tools/skills and Wizard MCP

## 1. Install Global Vibe CLI

```bash
curl -fsSL https://vibe.mistral.ai/install.sh | sh
```

Verify:

```bash
vibe --version
```

## 2. Prepare Project Environment

From repo root:

```bash
uv venv venv
uv sync --extra udos-wizard
```

## 3. Validate Local Vibe Config

Project config is committed in `.vibe/config.toml`.

Canonical MCP launcher values:

- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`

Canonical MCP activation command (cross-platform):

```bash
uv run --project . scripts/mcp_activation.py enable
```

## 4. Trust and Launch

From repo root:

```bash
vibe trust
vibe
```

## 5. Quick Health Checks

### MCP process check

```bash
uv run --project . wizard/mcp/mcp_server.py --tools
```

### Skill/tool path check

Ensure these paths exist:

- `vibe/core/skills/ucode`
- `vibe/core/tools/ucode`

## Common Misconfigurations

### Symptom: MCP server fails to start

Fix:

```bash
uv sync --extra udos-wizard
uv run --project . scripts/mcp_activation.py status
uv run --project . wizard/mcp/mcp_server.py --tools
```

### Symptom: skills or tools do not appear in Vibe

Fix:

```bash
vibe trust
```

Then restart `vibe` from repo root.

### Symptom: mixed environments (`venv` and `.venv`)

Policy for this repo:

- Use `venv/` only
- Do not use `.venv/`

## Notes

- This guide supersedes old instructions that cloned `mistral-vibe` locally or used pip-editable local Vibe installs.
- Keep historical material in `docs/.compost/` only.
