# AI Provider Availability Discrepancy: Root Cause Analysis

**Date:** 2025-02-24
**Issue:** User reports difference between "what uDOS reports available" and "what is actually installed"
**Severity:** High — Causes user confusion and diverging TUI vs GUI behavior
**Impact:** Trust in system state reporting undermined

---

## Executive Summary

uDOS has **two separate, independent provider status-checking implementations** that answer **fundamentally different questions**:

| Component | Location | Checks | Question | Result Type |
|-----------|----------|--------|----------|-------------|
| **TUI** | `core/tui/ucode.py:1773` | Live Ollama API | "What models are loaded RIGHT NOW?" | Live runtime state |
| **GUI** | `wizard/routes/provider_routes.py:124` | Config files + CLI | "Was this provider previously configured?" | Configuration state |

**Result:** TUI and GUI report different availability because they're checking **different artifacts**.

---

## Technical Breakdown

### TUI Implementation: `_get_ok_local_status()` (ucode.py:1773)

```python
def _get_ok_local_status(self) -> dict[str, Any]:
    """Return OK local Vibe status (Ollama + model)."""
    endpoint = mode.get("ollama_endpoint", "http://127.0.0.1:11434")
    model = self._get_ok_default_model()
    tags = self._fetch_ollama_models(endpoint)  # ← LIVE HTTP GET to Ollama

    if not tags.get("reachable"):
        return {"ready": False, "issue": "ollama down", ...}

    models = tags.get("models") or []
    normalized_models = self._normalize_model_names(models)

    # Check if configured model exists in currently-loaded models
    if model and normalized_target.isdisjoint(normalized_models):
        return {"ready": False, "issue": "missing model", ...}

    return {"ready": True, ...}
```

**What it does:**
1. Gets default model from `ok_modes.json`
2. **Queries Ollama API directly:** `curl http://127.0.0.1:11434/api/tags` (via `_fetch_ollama_models()`)
3. **Checks live Ollama state:** Is endpoint reachable? Are loaded models correct?
4. Returns: TUI's actual runtime readiness

**Key insight:** TUI checks **what Ollama currently has loaded**

### `_fetch_ollama_models()` (ucode.py:1740)

```python
def _fetch_ollama_models(self, endpoint: str) -> dict[str, Any]:
    """Query Ollama tags endpoint."""
    url = endpoint.rstrip("/") + "/api/tags"  # http://127.0.0.1:11434/api/tags
    try:
        with warnings.catch_warnings():
            response = http_get(url, timeout=2)  # ← LIVE HTTP REQUEST
            data = response.get("json") if isinstance(response.get("json"), dict) else {}
        models = [m.get("name") for m in data.get("models", []) if m.get("name")]
        return {"reachable": True, "models": models}
    except HTTPError as exc:
        return {"reachable": False, "error": f"HTTP {exc.code or 0}"}
```

**Time-sensitive:** Returns what Ollama has loaded **at the exact moment of the query**

---

### GUI Implementation: `check_provider_status()` (provider_routes.py:124)

```python
def check_provider_status(provider_id: str) -> dict[str, object]:
    """Check if a provider is configured and working."""
    provider = PROVIDERS.get(provider_id)

    # Check 1: Is CLI installed? (e.g., `which ollama`)
    cli_installed = shutil.which(provider.cli or "") is not None

    # Check 2: Does config file exist?
    configured = provider.config_file.exists() if provider.config_file else False

    # Check 3: Are API keys in secret store?
    available = _secret_available(provider.secret_key)

    # Special: GitHub runs 'gh auth status'
    # Special: API keys check both nested + flat config structures

    return {
        "configured": configured,
        "available": available,
        "cli_installed": cli_installed,
        "needs_restart": False,
        "enabled": is_enabled
    }
```

**What it does:**
1. Checks if CLI binary is installed (filesystem check: `shutil.which()`)
2. Checks if config file exists (filesystem check: file presence)
3. Checks if API keys are stored (filesystem check: secret store)
4. Returns: **configuration state**, not runtime state

**Key insight:** GUI checks **what's been previously set up**, not **what's currently running**

---

## Root Causes of Mismatch

### Scenario 1: "Installed But Offline"
```
TUI reports: ⚠️ "ollama down"
GUI reports: ✅ "available" (cli_installed=True, secret configured)

Why:
  • Ollama process is not running
  • TUI queries HTTP endpoint → timeout → "ollama down"
  • GUI checks CLI binary exists and config file present → "available"
  • User confusion: "But GUI says it's installed!"
```

### Scenario 2: "Configured But Not Loaded"
```
TUI reports: ⚠️ "missing model" (wanted: mistral, loaded: [])
GUI reports: ✅ "available" (config says setup complete)

Why:
  • Wizard setup completed, config saved
  • Ollama process running but models not yet pulled
  • TUI queries `/api/tags` → gets empty model list → "missing model"
  • GUI checks config file → "available"
  • User confusion: "Setup said it was ready!"
```

### Scenario 3: "New Model Not Detected"
```
User pulls model via Wizard: `ollama pull mistral`
TUI reports: ⚠️ "missing model" (checks old cached list)
GUI reports: ✅ "available" (checks config, not live models)

Why:
  • Wizard completes pull, saves to config
  • TUI cached old model list from startup
  • No mechanism for TUI to refresh after model pull
  • User confusion: "But I just installed it!"
```

### Scenario 4: "Process Crashed but Config Intact"
```
Ollama process crashes or is killed
TUI reports: ⚠️ "ollama down" or "model missing"
GUI reports: ✅ "available"

Why:
  • Configuration files are unchanged
  • Ollama process is gone
  • TUI checks live state → fails
  • GUI checks config → passes
  • User confusion: Divergent reporting
```

---

## Architectural Problem

### Current System (Broken)

```
TUI Startup
  └─ _show_ai_startup_sequence()
      ├─ _get_ok_local_status()        ← Checks LIVE Ollama
      │   └─ _fetch_ollama_models()    ← HTTP GET :11434/api/tags
      └─ _get_ok_cloud_status()         ← Checks Wizard health endpoint

Wizard Routes
  └─ /api/wizard/provider-status       ← Checks CONFIG FILES
      └─ check_provider_status()        ← shutil.which(), file.exists()

No Connection Between Them!
  • TUI doesn't call Wizard's check_provider_status()
  • Wizard doesn't watch Ollama port for changes
  • No shared canonical state source
  • No synchronization on model/provider changes
```

### Why They're Completely Separate

1. **Different Use Cases**
   - TUI: "Can I use AI right now?" (runtime check)
   - GUI: "What's been installed?" (inventory check)

2. **Design Isolation**
   - TUI (`core/tui/`) doesn't depend on Wizard (`wizard/`)
   - TUI is runnable offline without Wizard running
   - Wizard is separate HTTP server

3. **State Independence**
   - TUI checks live Ollama endpoint (ephemeral)
   - GUI checks persistent config files (state)
   - No sync mechanism between them

4. **No Central Handler**
   - `CoreProviderRegistry` exists but is for **Wizard services**, not **AI provider availability**
   - ProviderType enum has 9 types: `PORT_MANAGER`, `LIBRARY_MANAGER`, etc. — **No `OLLAMA_MODELS` or `AI_PROVIDER` type**
   - No `ProviderType.VIBE_STATUS` or similar
   - Registry is for plugins/extensions, not provider health checking

---

## Impact on User

1. **Startup Confusion**
   - TUI shows "ollama down" but Wizard says "available"
   - User doesn't know which to trust
   - Increases support questions

2. **Setup Validation Breaks**
   - SETUP command completes (config written)
   - TUI still shows "missing model"
   - User thinks SETUP failed

3. **Model Management Broken**
   - User pulls model via Wizard
   - TUI not updated until manual restart
   - No live refresh of model availability

4. **No Single Source of Truth**
   - Two different "is AI ready" decisions
   - Can disagree during transitions
   - No canonical "provider availability" definition

---

## Proposed Solution (3-Phase)

### Phase 1: Unified Provider Status Service (2-3h)

Create **single AI provider status source** that both TUI and Wizard call:

```python
# core/services/ai_provider_status_service.py

class AIProviderStatus(BaseModel):
    """Unified provider status across TUI and Wizard."""
    provider_id: str  # "ollama", "mistral", etc.
    is_configured: bool  # Config files/keys exist
    is_running: bool  # Process actually running
    is_available: bool  # Can be used right now
    models_loaded: list[str]  # What's actually loaded
    issue: str | None  # Why not available
    last_checked: datetime

class AIProviderStatusService:
    """Check both configuration AND runtime state."""

    @staticmethod
    def check_provider(provider_id: str) -> AIProviderStatus:
        """
        Unified check: configuration + runtime.
        Returns combined state: is_running, is_available, models_loaded.
        """
        # 1. Check configuration (what's setup)
        config_status = _check_config(provider_id)

        # 2. Check runtime (what's actually running)
        runtime_status = _check_runtime(provider_id)

        # 3. Combine: configured but offline? Misconfigured but running?
        return AIProviderStatus(
            is_configured=config_status.configured,
            is_running=runtime_status.running,
            is_available=config_status.configured and runtime_status.running,
            models_loaded=runtime_status.models,
            issue=_determine_issue(config_status, runtime_status)
        )
```

**Usage:**
- TUI calls: `AIProviderStatusService.check_provider("ollama")`
- Wizard calls: `AIProviderStatusService.check_provider("ollama")`
- Both get **same unified answer**

### Phase 2: Extend CoreProviderRegistry (1-2h)

Add AI provider types to `CoreProviderRegistry`:

```python
# core/services/provider_registry.py

class ProviderType(Enum):
    # ... existing types ...
    AI_VIBE_LOCAL = "ai_vibe_local"       # Ollama/local models
    AI_VIBE_CLOUD = "ai_vibe_cloud"       # Mistral/cloud API
    AI_PROVIDER_STATUS = "ai_provider_status"  # Status checking service
```

**Registration:**
```python
# Wizard startup
CoreProviderRegistry.register(
    ProviderType.AI_PROVIDER_STATUS,
    AIProviderStatusService,
    description="Unified AI provider status checking"
)
```

### Phase 3: IO Phase Synchronization (2-3h)

Implement file watchers for provider setup changes:

```python
# core/services/provider_watch_service.py

class ProviderWatchService:
    """Watch for provider configuration changes."""

    def watch_ollama_models(self):
        """Watch Ollama port for model changes."""
        # Watch :11434/api/tags every 30s
        # Broadcast changes to TUI via WebSocket

    def watch_setup_flags(self):
        """Watch provider_setup_flags.json changes."""
        # File watcher for wizard/config/provider_setup_flags.json
        # Broadcast to TUI when provider setup completes
```

**Result:**
- TUI subscribed to provider change events
- Auto-refresh model list when new model pulled
- Notify user "Model now available" immediately

---

## No Central OK Handler Found

**User asked:** "Do we have a central OK Handler?"

**Answer:** NO

- `ok_handler.py` **does not exist** (searched: no results)
- OK functionality scattered:
  - `_get_ok_local_status()` in `core/tui/ucode.py:1773`
  - `check_provider_status()` in `wizard/routes/provider_routes.py:124`
  - `_get_ok_cloud_status()` in `core/tui/ucode.py:1622`
  - Model pulling in `wizard/routes/ollama_routes.py`
  - Model list in `wizard/routes/ollama_route_utils.py`

**Legacy test artifact:** `test-packages` references `ok_handler.py` but file never existed (cleanup needed)

---

## Recommendation

**Phase 1 is critical** — Without unified provider status, TUI and GUI will continue reporting different availability.

Implement `AIProviderStatusService` as single source of truth:
1. Check **both** config AND runtime state
2. Return **unified** response both TUI and GUI call
3. Deploy to both `core/services/` (TUI-accessible) and Wizard routes

**This solves the mismatch without breaking existing code.**

