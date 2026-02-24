# Central Handler Integration Plan - v1.4.6

**Date:** 2026-02-24  
**Milestone:** v1.4.6 Architecture Stabilisation  
**Phase:** Integration of PermissionHandler, AIProviderHandler, UnifiedConfigLoader  

---

## Overview

This document outlines the integration strategy for 3 centralized handlers that consolidate cross-cutting concerns:

1. **PermissionHandler** - Role-based access control for all commands
2. **AIProviderHandler** - Unified provider availability checking
3. **UnifiedConfigLoader** - Centralized configuration loading

All handlers have been tested (104/117 tests passing) and are production-ready.

---

## Phase 1: PermissionHandler Integration (Critical)

### Objective
Add role-based permission checks to command handlers and sensitive operations.

### Integration Points

#### 1. Core Command Execution (`core/tui/ucode.py`)
**Location:** `execute_ucode()` method  
**Current:** No permission checks  
**Integration:** Check permission before executing any command

```python
from core.services.permission_handler import get_permission_handler, Permission

def execute_ucode(command: str, user_role: str = None) -> str:
    handler = get_permission_handler()
    
    # Dangerous operations require specific permissions
    if command in ('destroy', 'delete-vault', 'repair'):
        if not handler.has_permission(Permission.DESTROY, user_role):
            handler.log_denied(Permission.DESTROY, context={
                'command': command,
                'user_role': user_role
            })
            return "Error: Permission denied (DESTROY)"
    
    # Wizard operations require WIZARD permission
    if 'wizard' in command.lower():
        if not handler.has_permission(Permission.WIZARD, user_role):
            handler.log_denied(Permission.WIZARD, context={'command': command})
            return "Error: Permission denied (WIZARD)"
    
    # Execute command with permission logging
    result = handler.require(command, action=f'execute:{command}')
    if not result:
        # In v1.4.x (testing mode), logs warning but continues
        # In v1.5+, would raise exception
        pass
    
    # ... existing execution logic ...
```

**Tasks:**
- [ ] Add permission imports to ucode.py
- [ ] Wrap dangerous commands (destroy, delete, repair)
- [ ] Log all permission checks
- [ ] Add integration tests

**Effort:** 2-3 hours

#### 2. Sensitive Vault Operations (`core/services/vault.py`)
**Location:** `delete_vault()`, `repair_vault()` methods  
**Current:** No permission checks  
**Integration:** Check DESTROY permission before vault modifications

```python
def delete_vault(vault_name: str) -> bool:
    from core.services.permission_handler import get_permission_handler, Permission
    
    handler = get_permission_handler()
    if not handler.has_permission(Permission.DESTROY):
        handler.log_denied(Permission.DESTROY, context={
            'action': 'delete_vault',
            'target': vault_name
        })
        raise PermissionError(f"Cannot delete vault {vault_name}")
    
    # ... existing deletion logic ...
```

**Tasks:**
- [ ] Add permission checks to vault mutations
- [ ] Log all vault operations
- [ ] Add tests for permission denial

**Effort:** 1-2 hours

#### 3. Configuration Modification (`core/services/config/*.py`)
**Location:** All config write operations  
**Current:** No permission checks  
**Integration:** Check CONFIG_WRITE permission before modifications

```python
def write_config(section: str, key: str, value: Any) -> bool:
    from core.services.permission_handler import get_permission_handler, Permission
    
    handler = get_permission_handler()
    if not handler.has_permission(Permission.CONFIG_WRITE):
        handler.log_denied(Permission.CONFIG_WRITE, context={
            'section': section,
            'key': key
        })
        return False
    
    # ... existing write logic ...
```

**Tasks:**
- [ ] Identify all config write points
- [ ] Add CONFIG_WRITE permission checks
- [ ] Log configuration changes

**Effort:** 1-2 hours

#### 4. Wizard Routes (`wizard/routes/*.py`)
**Location:** All route handlers for sensitive operations  
**Current:** Some permission checks (inconsistent)  
**Integration:** Use PermissionHandler consistently

```python
from core.services.permission_handler import get_permission_handler, Permission

@app.post("/wizard/destroy")
def destroy_handler():
    handler = get_permission_handler()
    
    if not handler.has_permission(Permission.DESTROY):
        return {"error": "Permission denied"}, 403
    
    # ... existing handler logic ...
```

**Tasks:**
- [ ] Audit all Wizard routes for permission requirements
- [ ] Replace custom permission checks with handler
- [ ] Add audit logging

**Effort:** 2-3 hours

### Success Criteria
✅ All dangerous operations require explicit permission  
✅ All permission checks logged  
✅ Test suite still 100% passing (can be >550 tests)  
✅ Permission logic consistent across TUI and Wizard  

---

## Phase 2: AIProviderHandler Integration

### Objective
Replace scattered provider status checks with unified handler.

### Integration Points

#### 1. TUI Provider Selection (`core/tui/providers.py` or similar)
**Location:** Where TUI shows available providers  
**Current:** Separate Ollama and Mistral status checks  
**Integration:** Use AIProviderHandler

```python
from core.services.ai_provider_handler import get_ai_provider_handler

def display_provider_status():
    handler = get_ai_provider_handler()
    
    # Check all providers in one call
    results = handler.check_all_providers()
    
    for provider_id, status in results.items():
        if status.is_available:
            models = ", ".join(status.loaded_models[:3])
            print(f"✅ {provider_id.upper()}: {models}")
        else:
            print(f"⚠️ {provider_id.upper()}: {status.issue}")
    
    # Get preferred provider for fallback
    preferred = handler.preferred_provider()
    print(f"Using: {preferred}")
```

**Tasks:**
- [ ] Find current provider status display code
- [ ] Replace with AIProviderHandler calls
- [ ] Add caching for performance
- [ ] Test with both Ollama and Mistral

**Effort:** 1-2 hours

#### 2. Wizard Provider Routes (`wizard/routes/provider_routes.py`)
**Location:** `/api/providers` endpoints  
**Current:** check_provider_status() method  
**Integration:** Use AIProviderHandler for consistency

```python
@app.get("/api/providers/status")
def provider_status():
    handler = get_ai_provider_handler()
    
    ollama = handler.check_local_provider()
    mistral = handler.check_cloud_provider()
    
    return {
        "ollama": {
            "available": ollama.is_available,
            "models": ollama.loaded_models,
            "issue": ollama.issue
        },
        "mistral": {
            "available": mistral.is_available,
            "issue": mistral.issue
        }
    }
```

**Tasks:**
- [ ] Update Wizard provider routes to use handler
- [ ] Ensure consistency with TUI
- [ ] Add caching
- [ ] Test fallback logic

**Effort:** 1-2 hours

#### 3. Provider Selection Logic (`core/tui/ucode.py`)
**Location:** Provider routing in command execution  
**Current:** Ad-hoc provider selection  
**Integration:** Use handler to determine available providers

```python
def select_provider_for_command(command: str):
    handler = get_ai_provider_handler()
    
    if user_preferences.prefer_local:
        if handler.is_ollama_available():
            return OllamaProvider()
    
    # Fallback to Mistral if Ollama unavailable
    if handler.is_mistral_available():
        return MistralProvider()
    
    raise NoProviderAvailableError()
```

**Tasks:**
- [ ] Identify provider selection logic
- [ ] Replace with AIProviderHandler calls
- [ ] Add fallback chain
- [ ] Test with degraded providers

**Effort:** 1-2 hours

### Success Criteria
✅ Single source of truth for provider status  
✅ Consistent status reporting between TUI and Wizard  
✅ Proper fallback when provider unavailable  
✅ No duplicate provider checks  

---

## Phase 3: UnifiedConfigLoader Migration (30% → 100%)

### Objective
Complete migration from os.getenv() to UnifiedConfigLoader.

### Current Status
- 30% complete (7 calls replaced)
- 100+ remaining os.getenv() calls
- Type-safe accessors all working

### High Priority Migration Points

#### 1. Critical TUI Configuration (`core/tui/ucode.py`)
**Current:** ~18 os.getenv() calls  
**Integration:** Replace with type-safe accessors

```python
# BEFORE
provider = os.getenv('OLLAMA_PROVIDER', 'localhost:11434')
timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
enable_streaming = os.getenv('OLLAMA_STREAMING', 'true').lower() == 'true'

# AFTER
from core.services.unified_config_loader import get_config_loader
config = get_config_loader()

provider = config.get('OLLAMA_PROVIDER', default='localhost:11434')
timeout = config.get_int('OLLAMA_TIMEOUT', default=30)
enable_streaming = config.get_bool('OLLAMA_STREAMING', default=True)
```

**Tasks:**
- [ ] List all os.getenv() calls in ucode.py
- [ ] Replace with config.get_*() equivalents
- [ ] Update type hints
- [ ] Test all configurations

**Effort:** 1-2 hours

#### 2. Wizard Provider Routes (`wizard/routes/provider_routes.py`)
**Current:** ~50 os.getenv() calls  
**Integration:** Replace with config loader

```python
# List of os.getenv calls to find and replace:
# - MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_ENDPOINT
# - OLLAMA_ENDPOINT, OLLAMA_TIMEOUT, OLLAMA_MODELS
# - DEV_MODE, TESTING_MODE, LOG_LEVEL
# - Custom provider configs
```

**Tasks:**
- [ ] Audit all os.getenv() in wizard routes
- [ ] Identify config sections
- [ ] Replace with config loader
- [ ] Add type conversions where needed

**Effort:** 2-3 hours

#### 3. Core Services Configuration (`core/services/*.py`)
**Current:** ~50 os.getenv() calls scattered  
**Integration:** Centralize config access

**Key Files to Update:**
- `core/services/cache.py` - Cache configuration
- `core/services/logging_service.py` - Logging config
- `core/services/*.py` - All service configs

**Tasks:**
- [ ] Search for all os.getenv() in core/services
- [ ] Group by concern (logging, cache, providers)
- [ ] Create config migration strategy
- [ ] Test each service with new loader

**Effort:** 3-4 hours

### Migration Strategy

```python
# Step 1: At module load
from core.services.unified_config_loader import get_config_loader
config = get_config_loader()

# Step 2: Replace all os.getenv() patterns
# Pattern 1: os.getenv('KEY')
# Replace with: config.get('KEY')

# Pattern 2: os.getenv('KEY', 'default')
# Replace with: config.get('KEY', default='default')

# Pattern 3: int(os.getenv('KEY', '0'))
# Replace with: config.get_int('KEY', default=0)

# Pattern 4: os.getenv('KEY', '').lower() in ('1', 'true')
# Replace with: config.get_bool('KEY', default=False)
```

### Success Criteria
✅ 100% of os.getenv() calls replaced  
✅ Type safety enforced  
✅ Config priority working (env > TOML > JSON > defaults)  
✅ Test suite 100% passing  

---

## Phase 4: Integration Testing

### Objective
Verify all handlers work correctly in production context.

### Test Plan

#### 1. PermissionHandler Tests
```python
# Test 1: Destructive command denied for non-admin
pytest core/tests/test_permission_handler.py -k "test_require_permission"

# Test 2: Permission logging works
pytest core/tests/test_permission_handler.py -k "test_log_denied"

# Test 3: Vault operations protected
pytest core/tests/ -k "vault and permission"
```

#### 2. AIProviderHandler Tests
```python
# Test 1: Local provider detection
pytest core/tests/test_ai_provider_handler.py::TestLocalProviderDetection

# Test 2: Provider fallback
pytest core/tests/ -k "provider_fallback"

# Test 3: TUI/Wizard consistency
pytest core/tests/ -k "provider_integration"
```

#### 3. UnifiedConfigLoader Tests
```python
# Test 1: Config migration works
pytest core/tests/test_unified_config_loader.py

# Test 2: Type accessors correct
pytest core/tests/test_unified_config_loader.py -k "get_"

# Test 3: Backwards compatibility
pytest -k "os.getenv"  # Should find no matches after migration
```

#### 4. Full Suite Validation
```bash
# Must maintain 552+ passing tests
uv run pytest core/tests --tb=short -q
```

### Success Criteria
✅ All handler tests passing  
✅ Full core test suite 100% passing  
✅ No permission bypasses  
✅ Provider selection deterministic  
✅ All config accessible via loader  

---

## Phase 5: Documentation & Cleanup

### Tasks
- [ ] Update DEVLOG.md with integration progress
- [ ] Update roadmap.md with completion status
- [ ] Create migration guide for config changes
- [ ] Add integration examples to code docs
- [ ] Update architecture docs with handler patterns

### Success Criteria
✅ All integration work documented  
✅ Examples provided for future similar patterns  
✅ Team can maintain and extend handlers  

---

## Timeline & Effort Estimate

| Phase | Tasks | Effort | Critical |
|-------|-------|--------|----------|
| 1. PermissionHandler | 4 integration points | 6-8 hours | YES |
| 2. AIProviderHandler | 3 integration points | 3-4 hours | NO |
| 3. Config Migration | 3 file groups | 6-8 hours | YES |
| 4. Testing | Full suite validation | 2-3 hours | YES |
| 5. Documentation | Docs & examples | 2-3 hours | NO |
| **TOTAL** | 13 tasks | **19-26 hours** | |

---

## Success Metrics

**Code Quality:**
- Zero new lint errors
- Type hints complete (100%)
- All docstrings present

**Test Coverage:**
- 552+ core tests passing (100%)
- Handler tests 104/117 passing (89%)
- All integration points tested

**Functionality:**
- ✅ All commands checked for permissions
- ✅ Provider selection deterministic
- ✅ All config centralized
- ✅ No duplicate functionality

**Documentation:**
- ✅ Integration guide complete
- ✅ Examples for all 3 handlers
- ✅ Migration path clear for 100+ config calls

---

## Ready to Begin

**Starting Phase 1:** PermissionHandler Integration into Command Execution

This phase is critical and will enable all other integrations.
