# Centralization Implementation Guide

Created 3 central handlers to replace scattered implementations across TUI and Wizard.

## Status: Implementation in Progress

### Created (Ready)

✅ **core/services/permission_handler.py**
- Centralized permission checking for TUI + Wizard
- Replace: 47+ scattered permission checks
- Usage: `from core.services.permission_handler import get_permission_handler, Permission`

✅ **core/services/ai_provider_handler.py**
- Unified AI provider status checking (local + cloud)
- Replace: `_get_ok_local_status()`, `_get_ok_cloud_status()`, `check_provider_status()`
- Usage: `from core.services.ai_provider_handler import get_ai_provider_handler`

✅ **core/services/unified_config_loader.py**
- Central configuration loading (.env → TOML → JSON → defaults)
- Replace: 47+ `os.getenv()` calls
- Usage: `from core.services.unified_config_loader import get_config_loader`

---

## Migration Plan

### Phase 1: TUI Updates

**Files to Update:**
- `core/tui/ucode.py` — Remove `_get_ok_local_status()`, `_get_ok_cloud_status()`, `_fetch_ollama_models()`
- `core/tui/ucode.py` — Replace scattered `os.getenv()` with `get_config_loader()`
- Other TUI files — Replace `os.getenv()` with config loader

**Changes:**
```python
# BEFORE
status = self._get_ok_local_status()
dev_mode = os.getenv("UDOS_DEV_MODE", "0")

# AFTER
from core.services.ai_provider_handler import get_ai_provider_handler
from core.services.unified_config_loader import get_bool_config

status = get_ai_provider_handler().check_local_provider()
dev_mode = get_bool_config("UDOS_DEV_MODE")
```

### Phase 2: Wizard Routes Updates

**Files to Update:**
- `wizard/routes/provider_routes.py` — Replace `check_provider_status()`
- `wizard/routes/ucode_ok_routes.py` — Use new handler
- Other Wizard routes — Replace scattered permission checks

**Changes:**
```python
# BEFORE
def check_provider_status(provider_id: str) -> dict[str, object]:
    # 100+ lines of implementation

# AFTER
from core.services.ai_provider_handler import get_ai_provider_handler

@app.get("/api/provider/status/{provider_id}")
async def get_provider_status(provider_id: str):
    status = get_ai_provider_handler().check_local_provider()  # or check_cloud_provider()
    return status
```

### Phase 3: Permission Handler Integration

**Files to Update:**
- All handlers using permission checks
- Commands in `core/commands/` — Replace scattered checks
- Services in `core/services/` — Replace scattered checks

**Changes:**
```python
# BEFORE
from core.services.user_service import get_current_user
if not get_current_user().has_permission("admin"):
    self.logger.warning("Admin required")

# AFTER
from core.services.permission_handler import get_permission_handler, Permission
perms = get_permission_handler()
if not perms.require(Permission.ADMIN, action="destroy_vault"):
    return
```

### Phase 4: Cleanup Old Code

**Code to Remove:**
- `wizard/services/permission_guard.py` — Wizard-only version (replaced by core handler)
- `core/tui/ucode.py: _get_ok_local_status()` — ~70 lines
- `core/tui/ucode.py: _get_ok_cloud_status()` — ~30 lines
- `core/tui/ucode.py: _fetch_ollama_models()` — ~20 lines
- `wizard/routes/provider_routes.py: check_provider_status()` — ~150+ lines
- Duplicated config loading code across 6+ files

**Estimated Lines Removed:** 500-800 lines of duplicate code

---

## Files Needing Updates (By Priority)

### High Priority (Direct Usage)

1. **core/tui/ucode.py** (3834 lines)
   - Lines 1622-1710: Remove `_get_ok_cloud_status()`
   - Lines 1740-1772: Remove `_fetch_ollama_models()`
   - Lines 1773-1810: Remove `_get_ok_local_status()`
   - Lines ~1485+: Replace `os.getenv("UDOS_DEV_MODE")` with config loader
   - Multiple scattered `os.getenv()` calls for TUI settings

2. **wizard/routes/provider_routes.py** (575 lines)
   - Lines 124-200: Replace `check_provider_status()` implementation
   - Update all callers to use new handler
   - Remove import of `get_ok_local_status` from ucode.py

3. **wizard/routes/ucode_ok_routes.py**
   - Remove dependency on ucode._get_ok_local_status()
   - Use new AIProviderHandler instead

### Medium Priority (Config Loading)

4. **core/tui/ucode.py** (~47 os.getenv calls)
   - `UDOS_DEV_MODE`, `UDOS_TEST_MODE`, `UDOS_AUTOMATION`
   - `UDOS_TUI_*` (INVERT_HEADERS, CLEAN_STARTUP, STARTUP_EXTRAS, FORCE_STATUS)
   - `UDOS_QUIET`, `NO_ANSI`, `UDOS_NO_ANSI`
   - `VIBE_PRIMARY_PROVIDER`, `VIBE_SECONDARY_PROVIDER`
   - `UDOS_VIEWPORT_*` (COLS, ROWS)
   - `UDOS_HOME_ROOT_ENFORCE`

5. **wizard/routes/* files** (~10+ os.getenv calls)
   - `WIZARD_BASE_URL`, `WIZARD_PORT`, ports
   - Dev flags
   - API keys and secrets

6. **core/services/*.py** (Various config reads)
   - config_sync_service.py, user_service.py, settings.py
   - All should use unified loader

### Lower Priority (Consolidation)

7. **wizard/services/permission_guard.py**
   - Merge into core/services/permission_handler.py
   - Remove duplicate

8. **vibe/core/config.py** (623 lines)
   - Leave as-is (Vibe-specific, not uDOS core)
   - May eventually consolidate

9. **core/binder/config.py**
   - Leave as-is (Binder-specific)

---

## Testing Checklist

### Configuration Loader Tests

- [ ] Load .env file correctly
- [ ] Override .env with environment variables
- [ ] Load TOML config
- [ ] Load JSON configs (wizard.json, ok_modes.json)
- [ ] Path expansion (UDOS_ROOT, ~, variables)
- [ ] Boolean parsing (1/0, true/false, yes/no)
- [ ] All convenience functions work
- [ ] Caching works correctly
- [ ] Reload functionality works

### Permission Handler Tests

- [ ] Basic permission checks
- [ ] Role-based access control
- [ ] Multi-permission logic (any, all)
- [ ] Testing/alert-only mode
- [ ] Ghost mode integration
- [ ] Logging audit trail
- [ ] Singleton pattern works

### AI Provider Handler Tests

- [ ] Local Ollama detection (installed, running, models)
- [ ] Cloud Mistral detection (API key, reachable)
- [ ] Combined status (configured + running = available)
- [ ] Model normalization (tagged vs base names)
- [ ] Default model verification
- [ ] Issue determination
- [ ] TUI and Wizard get same response

### Integration Tests

- [ ] TUI startup uses new handlers
- [ ] Wizard API endpoints use new handlers
- [ ] Commands use permission handler
- [ ] Config changes reflected in commands
- [ ] No circular dependencies

---

## Commit Strategy

**Commit 1: Core handlers created**
```
feat: create 3 central handlers for permissions, AI providers, and config

- core/services/permission_handler.py: Unified permission checking
- core/services/ai_provider_handler.py: AI provider status (replaces scattered checks)
- core/services/unified_config_loader.py: Central configuration loading

No code changed yet; handlers are available for adoption.
```

**Commit 2-N: TUI migration**
```
refactor(tui): use centralized handlers for permissions, config, and AI provider status

- Replace _get_ok_local_status() with AIProviderHandler
- Replace os.getenv() calls with UnifiedConfigLoader
- Replace scattered permission checks with PermissionHandler
- Remove duplicate code from ucode.py
```

**Commit N+1: Wizard migration**
```
refactor(wizard): use centralized handlers for provider status and permissions

- Replace check_provider_status() with AIProviderHandler
- Update routes to use PermissionHandler
- Remove wizard/services/permission_guard.py (merged to core)
```

---

## Notes for Implementation

1. **No shims or adapters** — Replace directly, no intermediate wrappers
2. **Keep behavior identical** — All testing/alert-only mode behavior must be preserved
3. **Minimize imports** — Avoid circular dependencies
4. **Add logging** — All centralized handlers have logging for audit trails
5. **Cache wisely** — Config loader caches, providers check live + config
6. **Test thoroughly** — Each handler has clear test surfaces

---

## Success Criteria

✅ All 3 handlers created and importable
✅ No code broken during migration
✅ Permissions, config, and provider status centralized
✅ 500+ lines of duplicate code removed
✅ Single source of truth for each concern
✅ TUI and Wizard agree on provider availability
✅ Configuration changes propagate correctly
✅ All tests pass
