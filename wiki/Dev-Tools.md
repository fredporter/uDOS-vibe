# Dev Tools

**Version:** v1.4.4+
**Last Updated:** 2026-02-22

The **Dev** directory contains development tools, scripts, and testing utilities for uDOS.

---

## What's in Dev?

```
dev/
  __init__.py
  README.md
  bin/              # Utility scripts
  docs/             # Development documentation
  examples/         # Code examples
  scripts/          # Build and test scripts
  tests/            # Test suites
  tools/            # Development tools
```

> The exact contents can change across versions. Use the repo tree as the source of truth.

---

## Key Tools

### Build Tools

Development helpers live in `dev/` and module directories. Use repo scripts as available.

### Testing

Test suites are organized by module:

```bash
# Run specific tests
python -m pytest dev/tests/

# Run a shakedown script (if present)
python uDOS.py
```

### Examples

Sample code demonstrating uDOS features:

```
dev/examples/
  basic-commands/
  document-execution/
  extension-samples/
```

---

## Development Workflow

### 1. Setup Development Environment

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Or install as editable
uv pip install -e .
```

### 2. Make Changes

Follow the [AGENTS.md](../AGENTS.md) guidelines for Python code and documentation standards.

### 3. Test Changes

```bash
# Run tests with uv
uv run pytest

# Manual testing via Vibe CLI
vibe
# User: "/bash ucode HELP"

# Or direct shell commands
ucode HELP
ucode STATUS
```

### 4. Document Changes

Update relevant documentation in `docs/` and `wiki/`. Follow documentation guidelines in [AGENTS.md](../AGENTS.md).

---

## Development Standards

### Code Organization

- **vibe/:** Mistral Vibe CLI (upstream submodule)
- **core/:** Command infrastructure (stdlib Python only)
- **wizard/:** MCP server + web services (networking, AI routing)
- **sonic/:** Bootable USB tooling
- **dev/:** Development tools and tests

### Logging

Always use the centralized logger:

```python
from core.services.logging_manager import get_logger

logger = get_logger(__name__)
```

### Version Management

Never hardcode versions:

```bash
python -m core.version
```

---

## Available Tasks

VS Code tasks are configured for common operations:

- **Run uDOS Interactive** — Launch uDOS
- **Run Shakedown Test** — Full system test
- **Check Virtual Environment** — Verify setup

See `.vscode/tasks.json` for all available tasks.

---

## Next Steps

- **[Style Guide](../dev/docs/Style-Guide.md)** — Coding standards
- **[Architecture](Architecture.md)** — System design
- **[Contributors](Contributors.md)** — How to contribute
