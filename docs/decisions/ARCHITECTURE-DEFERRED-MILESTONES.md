# Architecture — Deferred Convergence Milestones

**Context:** Pre-release cleanup audit (2026-02-26).
**Completed commits:** `a03facd` (dead routes), `b85406c` (dup defs), `07ce276` (P4/P6/P7 convergence).
**Status:** 4 items deferred — each is a self-contained session.

---

## P2 — Remove dead `wizard.json` read from `UnifiedConfigLoader` ✅ trivial

**File:** `core/services/unified_config_loader.py` ~line 376
**Finding:** `_load_json_configs()` loads `wizard.json` into `_json_caches["wizard"]` but
nothing ever reads that cache. `WizardConfig.load()` is the only real consumer.
The unified loader's read is pure startup I/O waste.

**Fix:** Delete the 2-line tuple entry for `"wizard"` in `_load_json_configs()`.
**Risk:** None — the cached dict has zero callers.
**Time:** ~15 min.

---

## P5 — Fix circular import: `core/tui/ucode.py` → `wizard.services.provider_registry`

**File:** `core/tui/ucode.py` line 125
**Finding:** The two "provider registries" are *not* convergence candidates — they serve
different domains:
- `core/services/provider_registry.py::CoreProviderRegistry` → infrastructure services
  (port manager, plugin repo, monitoring, vibe service, secret store, rate limiter…)
- `wizard/services/provider_registry.py::VibeProviderRegistry` → AI model routing
  (Ollama, Mistral, OpenAI, Anthropic, Gemini); uses `vibe.core.provider_engine.ProviderType`

The real bug: `core/tui/ucode.py:125` directly imports `wizard.services.provider_registry`
— Core importing Wizard violates the dependency boundary.

**Fix:** Replace the direct wizard import in `ucode.py` with a lookup through
`CoreProviderRegistry.get(ProviderType.VIBE_SERVICE)`, which `wizard/server.py` already
registers at startup via `CoreProviderRegistry.auto_register_vibe()`.
**Risk:** Medium — `ucode.py` is the central TUI file. Good test coverage exists.
**Time:** ~1 hr.

---

## P1 — Consolidate `/health` and `/api/dashboard/health`

**Files:**
- `wizard/server.py` lines 619–632 — inline `GET /health` inside `_register_routes()`
- `wizard/routes/dashboard_summary_routes.py` lines 105–118 — `GET /api/dashboard/health`

**Current response shapes:**

| Field | `GET /health` | `GET /api/dashboard/health` |
|---|---|---|
| `status: "healthy"` | ✅ | ❌ |
| `version` | `WIZARD_SERVER_VERSION` | `_BRIDGE_VERSION` (hardcoded) |
| `timestamp` | Z-suffix format | no Z-suffix |
| `services` dict | ✅ | ❌ |
| `ok: true` | ❌ | ✅ |
| `bridge: "udos-wizard"` | ❌ | ✅ |
| `ollama_running` | ❌ | ✅ |

Note: `core/commands/health_handler.py` (TUI `HEALTH` command) is **not** an HTTP surface
— leave untouched.

**Fix:**
1. Extract `_health_probe(config)` from `dashboard_summary_routes.py` returning the merged schema.
2. Replace the inline `/health` handler in `server.py` with a delegate to `_health_probe`.
3. Consolidate to a single `version` source (`WIZARD_SERVER_VERSION`).
4. Normalise timestamp to always emit Z-suffix.

**Watch out:** Check test fixtures that assert on `/health` response fields before changing
the shape. If any external monitor/LB depends on `{"status": "healthy"}`, add a compat shim.
**Risk:** Medium — external API contract.
**Time:** ~2 hr.

---

## P3 — Unify notification history (own session — highest risk)

**Current state:** Two independent silos, incompatible storage.

| | `core/services/notification_history_service.py` | `wizard/services/notification_history_service.py` |
|---|---|---|
| Type | 4 module-level functions | `NotificationHistoryService` class, 15+ async methods |
| Storage | `memory/logs/notification-history.log` (JSONL) | `memory/notifications.db` (SQLite, 3 tables) |
| Callers | `system_script_runner.py` (×2), `todo_reminder_service.py` (×1) | `monitoring_manager.py`, `notification_history_routes.py`, `server.py` |
| Direct file readers | `automation_monitor.py`, `core/tui/ucode.py:2179` | — |

**Fix plan:**

1. **Define Protocol in core** (stdlib-only, no deps):
   ```python
   # core/services/notification_history_protocol.py
   class NotificationHistoryProtocol(Protocol):
       def record(self, entry: dict) -> None: ...
       def get_pending(self) -> dict | None: ...
   ```

2. **Migrate core callers** to accept the protocol via `CoreProviderRegistry`
   (add `ProviderType.NOTIFICATION_HISTORY` slot). Update `system_script_runner.py`
   and `todo_reminder_service.py`.

3. **Register wizard SQLite service** as the implementation in `wizard/server.py` startup.

4. **Update direct file readers** (`ucode.py:2179`, `automation_monitor.py`) to read
   from the service instead of the JSONL path.

5. **Decide on JSONL migration:** Does `memory/logs/notification-history.log` contain
   production data worth preserving? If yes, write a one-shot migration script.
   If no, stop writing to it and let it age out.

**Files touched:** `core/services/notification_history_protocol.py` (new),
`core/services/notification_history_service.py`, `core/services/system_script_runner.py`,
`core/services/todo_reminder_service.py`, `core/tui/ucode.py`,
`core/services/automation_monitor.py`, `core/services/provider_registry.py`,
`wizard/server.py`.
**Risk:** Highest — 8 files, storage backend change. Plan migration before coding.
**Time:** ~4 hr + migration script if needed.
