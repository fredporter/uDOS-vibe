# Phase 3: UnifiedConfigLoader Configuration Migration

**Status**: Starting
**Scope**: Replace 96 os.getenv() calls with UnifiedConfigLoader (get_config framework)
**Framework Status**: ✅ UnifiedConfigLoader ready (44/44 tests passing)
**Estimated Effort**: 6-8 hours

---

## Migration Pattern

### Pattern 1: Simple String Config
```python
# Before
value = os.getenv("KEY", "default")

# After
from core.services.unified_config_loader import get_config
value = get_config("KEY", "default")
```

### Pattern 2: Integer Config
```python
# Before
value = int(os.getenv("KEY", "10"))

# After
from core.services.unified_config_loader import get_config
value = get_config("KEY", 10, type=int)  # or
value = get_config_int("KEY", 10)
```

### Pattern 3: Boolean Config (from string flags)
```python
# Before
flag = os.getenv("KEY", "1").strip().lower() in {"1", "true", "yes"}

# After
from core.services.unified_config_loader import get_config_bool
flag = get_config_bool("KEY", True)
```

### Pattern 4: Optional Config (None if not set)
```python
# Before
value = os.getenv("KEY")  # Returns None if not set

# After
from core.services.unified_config_loader import get_config
value = get_config("KEY")  # Returns None if not set (default_value=None)
```

### Pattern 5: Multiple Fallback Values (or logic)
```python
# Before
role = (os.getenv("UDOS_USER_ROLE") or os.getenv("USER_ROLE") or "guest")

# After
from core.services.unified_config_loader import get_config
role = get_config("UDOS_USER_ROLE") or get_config("USER_ROLE") or "guest"
```

---

## Files to Migrate (Prioritized by os.getenv count)

### Priority 1: High-Impact Files (2-7 files, start here)

| # | File | Count | Estimated Effort | Notes |
|---|------|-------|------------------|-------|
| 1 | wizard/mcp/mcp_server.py | 9 | 20 min | MCP initialization, rate limiting |
| 2 | core/tui/form_fields.py | 9 | 20 min | Form field configuration |
| 3 | wizard/routes/self_heal_routes.py | 7 | 15 min | Self-healing provider routes |
| 4 | wizard/check_provider_setup.py | 6 | 15 min | Provider setup verification |
| 5 | wizard/services/setup_manager.py | 5 | 15 min | Wizard setup manager |
| 6 | wizard/services/path_utils.py | 4 | 10 min | Path utilities |
| 7 | wizard/services/admin_secret_contract.py | 4 | 10 min | Admin secret contract |

**Total for Priority 1: ~1.5 hours**

### Priority 2: Medium-Impact Files (8-12 files)

| # | File | Count | Estimated Effort |
|---|------|-------|------------------|
| 8 | wizard/mcp/gateway.py | 4 | 10 min |
| 9 | core/tui/renderer.py | 4 | 10 min |
| 10 | wizard/server.py | 3 | 8 min |
| 11 | wizard/services/secret_store.py | 2 | 5 min |
| 12 | wizard/services/interactive_console.py | 2 | 5 min |
| 13 | wizard/routes/ucode_routes.py | 2 | 5 min |
| 14 | wizard/routes/settings_unified.py | 2 | 5 min |
| 15 | core/tui/output.py | 2 | 5 min |

**Total for Priority 2: ~1 hour**

### Priority 3: Low-Impact Files (1-3 calls each)

- wizard/tools/check_secrets_tomb.py (1)
- wizard/services/wizard_auth.py (1)  
- wizard/services/wiki_provisioning_service.py (1)
- wizard/services/path_utils.py (1)

**Total for Priority 3: ~30 min**

### Note: Test Files (Skip for now)
- core/tests/test_unified_config_loader.py (5 calls - legitimate test usage)
- core/tests/v1_4_4_theme_command_test.py (2 calls - legitimate test usage)

These test files intentionally use os.getenv() to test the config loading behavior.

---

## Migration Workflow

### Phase 3A: Priority 1 Files (Start here)

**File 1: wizard/mcp/mcp_server.py**
- [ ] Review file structure
- [ ] Add `from core.services.unified_config_loader import get_config, get_config_bool, get_config_int`
- [ ] Replace 9 os.getenv() calls with appropriate get_config_*() methods
- [ ] Run tests to verify no regressions
- [ ] Commit with message

**File 2: core/tui/form_fields.py**
- [ ] Review file structure
- [ ] Add imports for get_config*
- [ ] Replace 9 os.getenv() calls
- [ ] Test and commit

**File 3: wizard/routes/self_heal_routes.py**
- [ ] Review file structure
- [ ] Replace 7 os.getenv() calls
- [ ] Test and commit

**File 4: wizard/check_provider_setup.py**
- [ ] Review and migrate 6 calls
- [ ] Test and commit

**File 5: wizard/services/setup_manager.py**
- [ ] Review and migrate 5 calls
- [ ] Test and commit

**File 6-7: Remaining Priority 1 Files**
- [ ] Path utils (4) and admin secret contract (4)
- [ ] Test and commit

### Phase 3B: Priority 2 & 3 Files

After Priority 1 is complete, migrate Priority 2 and 3 files following same pattern.

---

## Validation Strategy

### Per-File Validation
1. Run specific test files for that module (if exist)
2. Check for any import errors or missing dependencies
3. Verify config values are correctly retrieved

### Full Test Suite Validation
```bash
pytest core/tests --tb=short -q
```
Target: 652+ tests passing (no new failures)

### Integration Testing
- Manual spot-checks of migrated functionality
- Verify environment variable override still works
- Test with both env vars and config files

---

## Config Priority (Verification)

UnifiedConfigLoader follows this priority:
1. **Environment variables** (highest)
2. **pyproject.udos.toml** settings
3. **pyproject.toml** fallback
4. **Module defaults** (lowest)

Example:
```python
# If OLLAMA_HOST env var is set, it takes priority
# Otherwise looks in pyproject.udos.toml
# Then pyproject.toml
# Finally uses default "http://127.0.0.1:11434"
value = get_config("OLLAMA_HOST", "http://127.0.0.1:11434")
```

---

## Success Criteria

- [x] UnifiedConfigLoader framework ready and tested
- [ ] All 96 os.getenv() calls replaced (except test files)
- [ ] Zero new test failures in full suite
- [ ] All modules can still access config values correctly
- [ ] Environment variables still work for override

---

## Next Steps

1. ✅ Create this migration guide
2. 🔄 Start with Priority 1 files (wizard/mcp/mcp_server.py)
3. Complete Priority 1 set (~1.5 hours)
4. Complete Priority 2 & 3 (~1.5 hours)
5. Run full test suite validation
6. Document results in DEVLOG

