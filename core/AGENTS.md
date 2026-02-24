# AGENTS.md — Core Subsystem

Last Updated: 2026-02-24
Milestone: v1.4.6 Architecture Stabilisation Phase
Status: Stable

---

## Purpose

The `core` subsystem contains minimal, deterministic Python-only functionality.

Core provides:
- Command handling (ucode)
- Binder management
- Grid runtime
- State management
- Configuration loading
- Logging services
- Testing framework

---

## Architecture Rules

### Dependency Constraints

Core must use:
- Python stdlib only
- No external networking libraries
- No HTTP clients
- No cloud provider SDKs

Core may NOT:
- Access network resources
- Make external API calls
- Import from wizard/
- Duplicate wizard responsibilities

### Separation Boundary

```
core/          → Minimal, deterministic
wizard/        → Extended, networked
```

Core must never leak web or network logic.

---

## Runtime Model

Core operates in:
- CLI contexts
- TUI environments
- Offline-first mode
- Testing environments

Core must function without:
- Internet access
- External dependencies
- Provider credentials
- Web server

---

## Testing Requirements

- 100% unit test coverage for command handlers
- Mock all external integrations
- No network I/O in tests
- Fast execution (< 5 seconds for full suite)

---

## Logging Policy

All logs go through:

```python
from core.utils.logging_config import get_logger
logger = get_logger(__name__)
```

No direct print() statements in production code.
No custom logging frameworks.

---

## OK Agent Behaviour Constraints

When generating code for core:

- Do not import requests, httpx, aiohttp
- Do not import wizard modules
- Do not create networking logic
- Do not bypass ucode command layer
- Do not create shadow logging
- Respect stdlib-only constraint

If networking is needed → implement in wizard.

---

End of File
