# .env Refactoring Alignment Audit

**Status:** ⚠️ PARTIAL ALIGNMENT
**Date:** 2026-02-24
**Issue:** Codebase still reads moved variables from `.env` instead of `config.toml`

---

## Summary

The `.env` refactoring moved ~50 variables to `core/config/config.toml`, but **the codebase still reads most of these variables from `os.getenv()` directly**. This creates a gap: the config structure exists, but no code loads it.

**Action Required:** Create centralized config loader + update code to use it

---

## 1. Logging Configuration Mismatch

### Problem
**Location:** `core/services/logging_api.py:195-203`

Code reads logging config directly from environment:
```python
LogConfig(
    level=os.getenv("UDOS_LOG_LEVEL", "info").lower(),
    format=os.getenv("UDOS_LOG_FORMAT", "json").lower(),
    dest=os.getenv("UDOS_LOG_DEST", "file").lower(),
    redact=_coerce_bool(os.getenv("UDOS_LOG_REDACT"), True),
    categories=_split_csv(os.getenv("UDOS_LOG_CATEGORIES")),
    sampling=_safe_float(os.getenv("UDOS_LOG_SAMPLING"), 1.0),
    payloads=os.getenv("UDOS_LOG_PAYLOADS", "dev-only").lower(),
    ring_size=_safe_int(os.getenv("UDOS_LOG_RING"), 1000),
)
```

### Should Read From
`core/config/config.toml` → `[logging]` section

### Variables Affected
- `UDOS_LOG_LEVEL` → `logging.level`
- `UDOS_LOG_FORMAT` → `logging.format`
- `UDOS_LOG_DEST` → `logging.destination`
- `UDOS_LOG_REDACT` → `logging.redact`
- `UDOS_LOG_CATEGORIES` → `logging.categories`
- `UDOS_LOG_SAMPLING` → `logging.sampling`
- `UDOS_LOG_PAYLOADS` → `logging.payloads`
- `UDOS_LOG_RING` → `logging.ring_buffer`
- `UDOS_LOG_ROOT` → `logging.root` (also read in logging_api.py:124)

---

## 2. TUI Configuration Scattered

### Problem
Multiple TUI-related files read directly from `os.getenv()`:

| File | Variables | Lines |
|------|-----------|-------|
| `core/tui/renderer.py` | `UDOS_NO_ANSI`, `NO_COLOR` | 219 |
| `core/tui/form_fields.py` | `UDOS_TUI_INVERT_HEADERS` | 284, 622, 1228 |
| `core/tui/advanced_form_handler.py` | `UDOS_TUI_INVERT_HEADERS` | 739 |
| `core/tui/status_bar.py` | `UDOS_TUI_FULL_METERS` | 137 |
| `core/tui/ucode.py` | `UDOS_QUIET`, `UDOS_TUI_CLEAN_STARTUP`, `UDOS_TUI_STARTUP_EXTRAS`, `UDOS_TUI_FORCE_STATUS`, `UDOS_TUI_MAP_LEVEL` | 284, 908, 914, 1090, 2889 |
| `core/services/map_renderer.py` | `UDOS_TUI_INVERT_HEADERS` | 52 |
| `core/services/theme_service.py` | `UDOS_TUI_MAP_LEVEL`, `UDOS_TUI_LEGACY_REPLACEMENTS` | 247, 287 |

### Should Read From
`core/config/config.toml` → `[ui.tui]` + `[ui.tui.display]` sections

### Variables Affected
- `UDOS_QUIET` → `ui.tui.quiet`
- `UDOS_NO_ANSI` → `ui.tui.no_ansi`
- `UDOS_TUI_INVERT_HEADERS` → `ui.tui.display.invert_headers`
- `UDOS_TUI_FULL_METERS` → `ui.tui.display.full_meters`
- `UDOS_TUI_CLEAN_STARTUP` → `ui.tui.clean_startup`
- `UDOS_TUI_STARTUP_EXTRAS` → `ui.tui.display.startup_extras`
- `UDOS_TUI_FORCE_STATUS` → `ui.tui.display.force_status`
- `UDOS_TUI_MAP_LEVEL` → `ui.tui.display.map_level`

---

## 3. App Config Scattered

### Problem
**Location:** `core/commands/health_handler.py:326`

Code reads app config from environment:
```python
reserve_mb = self._safe_float(os.getenv("UDOS_COMPOST_RESERVE_MB"), default=512.0)
```

**Also:** `core/commands/ucode_handler.py`, `core/commands/script_handler.py` read env directly

### Should Read From
`core/config/config.toml` → `[app.cleanup]` section

### Variables Affected
- `UDOS_COMPOST_RESERVE_MB` → `app.cleanup.compost_reserve_mb`
- `UDOS_COMPOST_MAX_MB` → `app.cleanup.compost_max_mb`
- `UDOS_COMPOST_MAX_BYTES` → `app.cleanup.compost_max_bytes`
- `UDOS_VIEWPORT_COLS` → `app.viewport_cols`
- `UDOS_VIEWPORT_ROWS` → `app.viewport_rows`
- `OLLAMA_HOST` → `app.services.ollama_host`
- `VIBE_STREAM_DELAY_MS` → `app.services.stream_delay_ms`

---

## 4. Locale Configuration

### Problem
**Status:** No code currently reads locale from `.env`

But should consolidate if/when used:
- `UDOS_TIMEZONE` → `logging.timezone`
- `UDOS_LOCATION` → `logging.location`
- `UDOS_LOCATION_NAME` → `logging.location_name`
- `UDOS_GRID_ID` → `logging.grid_id`

### Note
These variables may not be actively used in current codebase. Check before implementing.

---

## 5. Secrets & User Data Path Issues

### Problem A: User Manager vs API Routes Path Mismatch

**User Manager** (`core/services/user_service.py:155`):
```python
self.users_file = self.state_dir / "users.json"  # → memory/bank/private/users.json
```

**API Routes** (`extensions/api/routes/settings.py:130`):
```python
user_json_path = project_root / "core" / "data" / "variables" / "user.json"  # Different!
```

### Problem B: Secrets Location Not Documented

**Current:** `wizard/secrets.tomb` (encrypted)
**Usage:** Referenced in docs but no code path constants defined

### Action Required
1. **Choose canonical location for user profiles:**
   - Option A: Use `memory/bank/private/users.json` (current for user_service)
   - Option B: Use `core/data/variables/user.json` (current for API)
   - Recommendation: **Option A** (memory/ = runtime state, not versioned data)

2. **Create path constants:**
   ```python
   # core/services/paths.py (new)
   USERS_FILE = Path(get_repo_root()) / "memory" / "bank" / "private" / "users.json"
   SECRETS_TOMB = Path(get_repo_root()) / "wizard" / "secrets.tomb"
   ```

3. **Update API routes** to use correct path (memory/bank not data/variables)

---

## 6. No Centralized Config Loader

### Problem
No single `core.services.config_loader` exists that:
- Loads `config.toml`
- Provides typed access to settings
- Falls back to `.env` for startup essentials

### Solution

Create `core/services/config_loader.py`:
```python
from pathlib import Path
import tomllib  # Python 3.11+
from typing import Any, Dict, Optional

class AppConfig:
    """Centralized config from core/config/config.toml"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            from core.services.logging_api import get_repo_root
            config_path = Path(get_repo_root()) / "core" / "config" / "config.toml"

        self.config_path = config_path
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load config.toml with fallback defaults"""
        if not self.config_path.exists():
            return self._defaults()

        with open(self.config_path, 'rb') as f:
            return tomllib.load(f)

    @staticmethod
    def _defaults() -> Dict[str, Any]:
        """Return default config structure"""
        return {
            'logging': {
                'level': 'INFO',
                'destination': 'file',
                'format': 'json',
                ...
            },
            'ui': { ... },
            'app': { ... },
        }

    # Typed accessors
    def log_level(self) -> str:
        return self.data.get('logging', {}).get('level', 'INFO')

    def tui_quiet(self) -> bool:
        return self.data.get('ui', {}).get('tui', {}).get('quiet', False)

    # ... more accessors
```

Then use:
```python
config = AppConfig()
log_level = config.log_level()  # Instead of os.getenv('UDOS_LOG_LEVEL')
```

---

## 7. What Still Belongs in `.env`

These variables are **startup-critical** and should stay in `.env`:
- `UDOS_ROOT` - Needed before Python can find config
- `VAULT_ROOT` - Framework paths needed at startup
- `VAULT_MD_ROOT` - Framework paths
- `USER_NAME` - Identity (set by SETUP story)
- `WIZARD_BASE_URL` - Server endpoint
- `UDOS_DEV_MODE`, `UDOS_TEST_MODE`, `UDOS_AUTOMATION` - Quick toggles

**These are correct and properly documented.**

---

## 8. Implementation Plan

### Phase 1: Create Config Loader (2-3 hours)
1. Create `core/services/config_loader.py`
2. Add typed accessor methods
3. Create `core/services/paths.py` for constants
4. Add unit tests

### Phase 2: Migrate Logging (1.5 hours)
1. Update `core/services/logging_api.py` to use `AppConfig`
2. Verify no regressions

### Phase 3: Migrate TUI Settings (2 hours)
1. Create TUI config accessor helper
2. Update all TUI files to use config loader
3. Test theme/display rendering

### Phase 4: Fix User Path (1.5 hours)
1. Update API routes to use `memory/bank/private/users.json`
2. OR update user_service to use `core/data/variables/users.json` (if that's preferred)
3. Create path constants
4. Add migration script if needed

### Phase 5: Consolidate Remaining (2 hours)
1. Migrate app cleanup/compost settings
2. Migrate locale settings (if used)
3. Final integration testing

**Total Estimate:** 8-10 hours

---

## 9. Post-Implementation Checklist

- [ ] `core/services/config_loader.py` created + tested
- [ ] `core/services/paths.py` created with constants
- [ ] All logging config reads from config object
- [ ] All TUI config reads from config object
- [ ] All app config reads from config object
- [ ] User path mismatch resolved (API + user_service align)
- [ ] Secrets.tomb path documented in code
- [ ] No hard-coded paths remain (use UDOS_ROOT)
- [ ] `.env` only has 10-15 startup essentials
- [ ] Config example file matches actual implementation
- [ ] New config structure documented in README.md

---

## See Also

- [config/README.md](core/config/README.md) - Current config structure
- [.env.example](.env.example) - Startup essentials (correct)
- [config.toml.example](core/config/config.toml.example) - App settings (not yet loaded)
