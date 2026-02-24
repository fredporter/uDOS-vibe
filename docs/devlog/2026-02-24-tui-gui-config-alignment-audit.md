# TUI vs GUI (Wizard) Configuration Alignment Audit
**Date:** 2026-02-24
**Status:** COMPLETE - Pre-centralization alignment check
**Scope:** TUI (core/tui), GUI (wizard routes), user data storage, secrets management

---

## Executive Summary

TUI and GUI **do not currently share the same environment variable sets**, creating multiple sources of truth and potential drift:

| Component | Config Method | Variables | Issues |
|-----------|---------------|-----------|--------|
| **TUI** (core/tui) | Direct `os.getenv()` scattered across 7+ files | 47 hardcoded env reads | Duplicate logic, scattered TUI settings |
| **GUI** (wizard routes) | Centralized route handlers + wizard.json config | JSON-based configuration | Different structure, separate API |
| **User Data** | TWO different locations | memory/bank/private/users.json vs core/data/variables/user.json | Path mismatch, data inconsistency |
| **Secrets** | wizard/secrets.tomb (encrypted) | API keys, tokens, admin credentials | Partially documented, no code constants |
| **Paths** | Environment variables + hardcoded | UDOS_ROOT, VAULT_ROOT, VAULT_MD_ROOT | No centralization, environment-dependent |

---

## 1. TUI (core/tui) Configuration Analysis

### 1.1 Environment Variables Read by TUI

**File:** `core/tui/ucode.py` (47 matches)

| Variable | Usage | Files | Issue |
|----------|-------|-------|-------|
| **UDOS_ROOT** | Repo root path | ucode.py:2102, form_fields.py:1368 | Fallback to repo_root, not always set |
| **VAULT_ROOT** | Vault location | ucode.py:2103, form_fields.py:1368, config_sync_service.py | Multiple fallback paths |
| **VAULT_MD_ROOT** | Alt vault path | ucode.py:2124 | Redundant with VAULT_ROOT |
| **USER_NAME** | Primary identity | .env | Used in setup flow |
| **USER_USERNAME** | Secondary identity | ucode.py:2119 | Duplicate naming |
| **WIZARD_BASE_URL** | Wizard endpoint | ucode.py (multiple) | Hardcoded fallback to http://localhost:8765 |
| **WIZARD_KEY** | Wizard authentication | ucode.py:2445, admin_secret_contract.py | Stored in both .env and secret store |
| **WIZARD_ADMIN_TOKEN** | Admin authentication | ucode.py:2445, admin_secret_contract.py | Stored in both .env and secret store |

### 1.2 TUI Display Settings (Duplicated Logic)

**Issue:** UDOS_TUI_INVERT_HEADERS is checked in **4 separate files** with identical logic:

```
core/tui/form_fields.py:284    ✓ Header inversion check
core/tui/form_fields.py:622    ✓ Header inversion check
core/tui/form_fields.py:1228   ✓ Header inversion check
core/tui/advanced_form_handler.py:739  ✓ Header inversion check
```

**Similar duplicates:**
- `UDOS_VIEWPORT_COLS` - checked in 5 locations (form_fields.py:252, 520, 771, 920, 1060)
- `NO_COLOR` and `UDOS_NO_ANSI` - checked in renderer.py:219 (2 checks)
- `UDOS_QUIET` - ucode.py:284 only
- `UDOS_LAUNCHER_BANNER` - ucode.py:1209 only
- `UDOS_DEV_MODE` - ucode.py:1485, wizard/services/permission_guard.py:7
- `UDOS_AUTOMATION` - ucode.py:965, 1408

### 1.3 TUI Configuration Files Read

| File | Purpose | Format |
|------|---------|--------|
| `.env` | Startup variables only | Key=value |
| Direct os.getenv() calls | TUI display settings | Environment-based |
| `core/config/config.toml.example` | App configuration template | TOML (not implemented) |

**Problem:** No code loads `config.toml` yet. TUI still reads 50+ settings from individual os.getenv() calls.

---

## 2. GUI (Wizard) Configuration Analysis

### 2.1 Wizard Configuration Routes

**File:** `wizard/routes/settings_unified.py` (unified settings - v1.1.0)

| Config Type | Location | Format | Access |
|-----------|----------|--------|--------|
| **Wizard Core** | `wizard/config/wizard.json` | JSON | `/api/config` |
| **Networking** | `wizard/config/wizard.json` | JSON (nested) | `/api/config/networking` |
| **Secrets** | `wizard/secrets.tomb` | Encrypted (TOML) | Secret store API |
| **Environment** | `.env` file | dotenv | `/api/config/env` (via settings route) |
| **User Data** | `core/data/variables/user.json` | JSON | `/api/settings/user-variables` |
| **Extension Config** | Per-extension | Various | `/api/config/extensions` |

### 2.2 Wizard Configuration Structure (wizard.json)

```json
{
  "host": "0.0.0.0",
  "port": 8765,
  "debug": false,
  "requests_per_minute": 60,
  "plugin_repo_enabled": true,
  "plugin_auto_update": false,
  "web_proxy_enabled": true,
  "ok_gateway_enabled": false,
  "github_webhook_secret": null,
  "admin_api_key_id": null,
  "icloud_enabled": false,
  "oauth_enabled": false,
  "compost_cleanup_days": 30,
  "memory_root": "memory",
  "memory_root_actual": "<resolved local path>"
}
```

### 2.3 Wizard API Endpoints for Configuration

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/config` | GET | Get wizard.json | JSON config |
| `/api/config` | PATCH | Update wizard.json | Updated JSON |
| `/api/config/env` | GET | Read .env variables | Key=value pairs |
| `/api/config/env` | POST | Set .env variable | Success/error |
| `/api/config/files` | GET | List config files | File metadata |
| `/api/config/{file_id}` | GET | Get specific config | File content |
| `/api/config/{file_id}` | POST | Save specific config | Success/error |
| `/api/config/export` | POST | Export configs | Transferable JSON |
| `/api/admin-token/generate` | POST | Create admin token | Token + stored secret |
| `/api/admin-token/status` | GET | Check token status | Current tokens |
| `/api/settings/user-variables` | GET | Get user.json | Variables from core/data/ |
| `/api/settings/user-variables/{key}` | POST | Set user variable | Success/error |

---

## 3. User Data Storage - CRITICAL ALIGNMENT GAP

### 3.1 Two Different Storage Locations

| Location | Used By | Format | Purpose | Issue |
|----------|---------|--------|---------|-------|
| `memory/bank/private/users.json` | `core/services/user_service.py:153` | JSON | User profiles, roles, sessions | ✓ Correct location (runtime state) |
| `core/data/variables/user.json` | `extensions/api/routes/settings.py:130` | JSON | User configuration variables | ❌ Wrong location (should be runtime) |

### 3.2 Data Structure Comparison

**memory/bank/private/users.json** (Runtime State)
```json
{
  "ghost": {
    "username": "ghost",
    "role": "guest",
    "created": "2026-01-01T00:00:00Z",
    "last_login": "2026-02-24T10:30:00Z"
  },
  "admin": {
    "username": "admin",
    "role": "admin",
    "created": "2026-01-15T00:00:00Z"
  }
}
```

**core/data/variables/user.json** (App Configuration - WRONG LOCATION)
```json
{
  "variables": {
    "preferred_theme": {
      "default": "dark",
      "type": "string"
    },
    "notification_frequency": {
      "default": "hourly",
      "type": "string"
    }
  }
}
```

### 3.3 Problem Statement

- `user_service.py` stores runtime user profiles at **memory/bank/private/users.json** ✓
- `settings.py` API reads/writes user *variables* at **core/data/variables/user.json** ❌
- These are **different concepts** but **API doesn't coordinate**
- Moving user data via TUI (memory/bank) doesn't reflect in API (core/data)
- **Decision needed:** Consolidate into single location

---

## 4. Secrets Management - Documentation Gap

### 4.1 Current Secrets Storage

| Secret Type | Location | Format | Access Method | Issue |
|-------------|----------|--------|---|-------|
| Wizard key | .env + wizard/secrets.tomb | Encrypted | admin_secret_contract.py | Stored in both places |
| Admin token | .env + wizard/secrets.tomb | Encrypted | admin_secret_contract.py | Stored in both places |
| API keys | wizard/secrets.tomb | Encrypted | SecretStore API | ✓ Centralized |
| Mistral key | wizard/secrets.tomb | Encrypted | SecretStore API | ✓ Centralized |
| GitHub token | wizard/secrets.tomb | Encrypted | SecretStore API | ✓ Centralized |

### 4.2 Secret Store Contract (wizard/services/admin_secret_contract.py)

```python
# Dual storage pattern (problematic)
wizard_key = env_values.get("WIZARD_KEY") or os.getenv("WIZARD_KEY", "").strip()
admin_token = env_values.get("WIZARD_ADMIN_TOKEN") or os.getenv("WIZARD_ADMIN_TOKEN", "").strip()

# Then stored in both places:
os.environ["WIZARD_KEY"] = wizard_key
os.environ["WIZARD_ADMIN_TOKEN"] = admin_token
store.set(entry)  # Also stored in secrets.tomb
```

**Problem:** Keys stored in both .env and tomb, creating sync inconsistency

### 4.3 Missing Documentation

| Item | Status | Location |
|------|--------|----------|
| Path to secrets.tomb | ✓ Known | wizard/secrets.tomb |
| Code constant for path | ❌ Missing | Should be in `core/services/paths.py` |
| Secret categories | ✓ Known | See wizard API endpoints |
| Encryption mechanism | ✓ Known | Uses secret_store module |
| Decryption by apps | ⚠️ Partial | TUI reads WIZARD_KEY from env; apps call service |

---

## 5. Paths - No Centralization

### 5.1 Core Paths Used

| Path | Variable | Used By | Fallback | Issue |
|------|----------|---------|----------|-------|
| Repo root | UDOS_ROOT | TUI, Wizard, API | `repo_root/` | Environment-dependent |
| Vault root | VAULT_ROOT | TUI, API, user_service | `UDOS_ROOT/memory/vault` | Inconsistent fallback |
| Vault MD | VAULT_MD_ROOT | TUI only | Falls back to VAULT_ROOT | Redundant |
| Memory root | — | wizard/services/path_utils.py | `memory/` | Hardcoded in code |
| Users file | — | user_service.py | `memory/bank/private/users.json` | No constant |
| Secrets file | — | admin routes | `wizard/secrets.tomb` | No constant |
| Config file | — | config routes | `wizard/config/wizard.json` | No constant |

### 5.2 Path Resolution Code (Scattered)

```python
# core/tui/ucode.py:2102
udos_root = os.getenv("UDOS_ROOT") or str(self.repo_root)

# core/services/user_service.py:153
state_dir = Path(get_repo_root()) / "memory" / "bank" / "private"

# wizard/services/path_utils.py:26
env_root = os.getenv("VAULT_ROOT")

# All inconsistent implementations
```

**Solution:** Create `core/services/paths.py` with constants:
```python
USERS_FILE = get_repo_root() / "memory" / "bank" / "private" / "users.json"
SECRETS_TOMB = get_repo_root() / "wizard" / "secrets.tomb"
VAULT_ROOT = Path(os.getenv("VAULT_ROOT")) or get_repo_root() / "memory" / "vault"
MEMORY_ROOT = get_repo_root() / "memory"
```

---

## 6. Identified Configuration Duplicates

### 6.1 TUI Header Inversion Logic

**Duplicate Pattern:** `UDOS_TUI_INVERT_HEADERS` checked identically 4 times

```python
# core/tui/form_fields.py:284
if os.getenv("UDOS_TUI_INVERT_HEADERS", "1").strip().lower() not in {"0", "false", "no"}:

# core/tui/form_fields.py:622
if os.getenv("UDOS_TUI_INVERT_HEADERS", "1").strip().lower() not in {"0", "false", "no"}:

# core/tui/form_fields.py:1228
if os.getenv("UDOS_TUI_INVERT_HEADERS", "1").strip().lower() not in {"0", "false", "no"}:

# core/tui/advanced_form_handler.py:739
if os.getenv("UDOS_TUI_INVERT_HEADERS", "1").strip().lower() not in {"0", "false", "no"}:
```

**Solution:** Extract to `core/tui/config.py`:
```python
def get_tui_invert_headers() -> bool:
    return os.getenv("UDOS_TUI_INVERT_HEADERS", "1").strip().lower() not in {"0", "false", "no"}
```

### 6.2 Viewport Columns Logic

**Duplicate Pattern:** `UDOS_VIEWPORT_COLS` checked 5 times

Files: form_fields.py:252, 520, 771, 920, 1060

**Solution:** Move to ViewportService (already exists partially)

### 6.3 NO_COLOR / ANSI Color Handling

**Duplicate Pattern:** Different color handling in renderer.py vs individual form fields

```python
# core/tui/renderer.py:219
if os.getenv("UDOS_NO_ANSI") == "1" or os.getenv("NO_COLOR"):

# core/tui/advanced_form_handler.py:639
if os.environ.get('NO_COLOR'):
```

**Solution:** Centralize in OutputToolkit or renderer

### 6.4 Dev Mode Checking

**Duplicate:** Checked in multiple places with different logic

```python
# core/tui/ucode.py:1485
if os.getenv("UDOS_DEV_MODE") in ("1", "true", "yes"):

# wizard/services/permission_guard.py:7
DEFAULT_ROLE = os.getenv("UDOS_DEFAULT_ROLE", "maintainer")
```

---

## 7. Wizard Config Pages - What's Missing

### 7.1 Settings UI Pages Needed

The wizard dashboard **should display** but doesn't document:

```
Dashboard Pages:
  ✓ Configuration
  ✓ Extensions
  ✓ Networking
  ✓ Admin Token
  ❌ User Data Locations (NEW)
  ❌ Private User Data (NEW)
  ❌ Vault/Memory Paths (NEW)
  ❌ Secrets Inventory (NEW)
  ❌ Config Sync Status (NEW)
```

### 7.2 Proposed "User Data & Paths" Configuration Page

Should show:

```
User Data Locations
├── Primary User File
│   └── memory/bank/private/users.json (current)
│   └── Profiles: admin, guest, demo, ...
│   └── Last sync: 2026-02-24 10:30 UTC
│
├── User Configuration Variables
│   └── ??? core/data/variables/user.json (or moved to memory/?)
│   └── Preferences: theme, notifications, ...
│   └── Last sync: [unknown]
│
├── Secrets Store
│   └── wizard/secrets.tomb (encrypted)
│   └── Keys: WIZARD_KEY, MISTRAL_API_KEY, GITHUB_TOKEN, ...
│   └── Last access: 2026-02-24 10:25 UTC
│
├── Vault Root
│   └── Path: /Users/fredbook/Code/uDOS-vibe/memory/vault
│   └── Size: 1.2 GB (calculated)
│   └── Last access: 2026-02-24 10:28 UTC
│
└── Memory Root
    └── Path: /Users/fredbook/Code/uDOS-vibe/memory
    └── Size: 3.4 GB
    └── Subdirs: bank/, logs/, tests/, story/, vault/, ...
    └── Last sync: [on demand]
```

### 7.3 Missing Configuration API Endpoints

```
GET /api/wizard/user-data-locations
  Returns: locations of all user data (current audit output)

GET /api/wizard/vault-info
  Returns: vault root path, size, contents summary

GET /api/wizard/memory-info
  Returns: memory root path, size, subdirectory structure

GET /api/wizard/secrets-inventory
  Returns: list of secret keys in tomb (without values)

POST /api/wizard/sync-user-data
  Ensures memory/bank/private/users.json and
  core/data/variables/user.json stay in sync
  (depends on audit decision re: consolidation)
```

---

## 8. Config Setting Seamless UI Pattern

### 8.1 Current Problem

Setting a configuration variable has **different code paths** depending on entry point:

```
TUI → Setting Variable
├─ Read from os.getenv()
├─ Write to... unclear (No code path found)
└─ Problem: No mechanism to persist changes within same session

GUI → Setting Variable (via /api/config/env)
├─ Read from .env file
├─ Write to .env file
├─ Refresh os.environ[]
└─ Problem: TUI doesn't catch changes made via GUI
```

### 8.2 Required Seamless Pattern

For variables to be settable from **both TUI and GUI**:

| Component | Read From | Write To | Sync |
|-----------|-----------|----------|------|
| TUI session | ConfigLoader (cached) | ConfigLoader + .env | FileWatch/Signal |
| GUI API | ConfigLoader + .env | ConfigLoader + .env | Built-in  |
| Environment | os.getenv → ConfigLoader fallback | ConfigSync hydration | Signal |

---

## 9. Recommendations for Centralization

### 9.1 Phase 1: Consolidate Paths (1-2 hours)

```
Create: core/services/paths.py

USERS_FILE = get_repo_root() / "memory" / "bank" / "private" / "users.json"
SECRETS_TOMB = get_repo_root() / "wizard" / "secrets.tomb"
VAULT_ROOT = Path(os.getenv("VAULT_ROOT")) or get_repo_root() / "memory" / "vault"
MEMORY_ROOT = get_repo_root() / "memory"
CONFIG_FILE = get_repo_root() / "wizard" / "config" / "wizard.json"

Replace all hardcoded paths with imports from this module.
```

### 9.2 Phase 2: Create TUI Configuration Helpers (2-3 hours)

```
Create: core/tui/config.py

def get_invert_headers() -> bool
def get_viewport_cols() -> int
def get_no_ansi() -> bool
def get_quiet_mode() -> bool
def get_dev_mode() -> bool
def get_launcher_banner() -> bool

Replace 20+ scattered os.getenv() calls with these helpers.
```

### 9.3 Phase 3: Decide User Data Consolidation (30 min - decision)

**Decision Point:**

Option A: Move user.json to memory/bank/private/
- Pro: All user data in runtime state folder
- Con: Requires API route migration

Option B: Keep separate (users profile vs configuration)
- Pro: Clear separation of concerns
- Con: Two locations to maintain

**Recommendation:** Option A - consolidate both at memory/bank/private/users.json

### 9.4 Phase 4: Config Sync for TUI ↔ GUI (3-4 hours)

```
Implement: ConfigSyncWatcher in core/services/

On TUI startup:
  - Load .env + config.toml + wizard.json into ConfigLoader
  - Watch for external changes (from GUI API)
  - Hot-reload on .env changes

On GUI API write:
  - Update .env file
  - Then signal ConfigSync to reload
  - Broadcast change to running TUI sessions (via WebSocket)
```

### 9.5 Phase 5: Wizard Config Pages (2-3 hours)

```
Add wizard routes for user data/paths inventory:

GET /api/wizard/data-locations
GET /api/wizard/vault-info
GET /api/wizard/memory-info
GET /api/wizard/secrets-inventory
POST /api/wizard/sync-user-data
```

---

## 10. Current Blockers for TUI ↔ GUI Seamless Config

| Blocker | Impact | Solution |
|---------|--------|----------|
| No TUI config write method | Can't change vars in TUI | Implement TUI config handler |
| No inter-process notification | Changes via GUI not seen by TUI | Add ConfigSyncWatcher |
| Two user data locations | Data can drift | Consolidate to memory/bank/private/ |
| Duplicate TUI setting logic | 20+ places to update | Extract to helpers |
| No code constants for paths | Hardcoded paths everywhere | Create paths.py |
| No centralized secret inventory | Can't list/verify secrets | Add secrets inventory API |
| Missing wizard config pages | User can't see data locations | Add wizard routes + UI |

---

## 11. Validation Checklist

### Before Centralization

- [ ] Confirm both TUI and wizard read identical .env variables
- [ ] Verify all hardcoded paths use new constants from paths.py
- [ ] Test that changing variable in GUI reflects in running TUI
- [ ] Confirm user data consolidation to memory/bank/private/
- [ ] Validate secrets.tomb is never duplicated in .env (only wizard key)
- [ ] Check that all 4 TUI header inversion calls use same helper
- [ ] Verify wizard config pages show all user data locations
- [ ] Test seamless config changes TUI → GUI → TUI

### After Centralization

- [ ] No more than 2 sources of truth for any config variable
- [ ] All path constants imported from core/services/paths.py
- [ ] All TUI config reads from config helpers, not os.getenv()
- [ ] User data stored in single location with API coordination
- [ ] Secrets inventory accessible from wizard config pages
- [ ] TUI reflects GUI changes without restart
- [ ] Profile matrix tests pass for all profiles

---

## 12. Implementation Order

1. **paths.py** - Foundation (1-2 hours)
2. **TUI config helpers** - Reduce duplicates (2-3 hours)
3. **User data consolidation** - Decision + migration (2-3 hours)
4. **ConfigSyncWatcher** - TUI ↔ GUI coordination (3-4 hours)
5. **Wizard config pages** - UI visibility (2-3 hours)
6. **Testing** - Profile matrix + integration (2-3 hours)

**Total:** 15-21 hours of work

---

## Appendix: Complete Variable Inventory

### TUI Variables (47 total)

```
UDOS_ROOT
VAULT_ROOT
VAULT_MD_ROOT
USER_NAME
USER_USERNAME
WIZARD_BASE_URL
WIZARD_KEY
WIZARD_ADMIN_TOKEN
UDOS_QUIET
UDOS_NO_ANSI
NO_COLOR
UDOS_EMOJI_TUI_RENDER
UDOS_STORY_FORM_TUI
UDOS_TUI_CLEAN_STARTUP
UDOS_TUI_STARTUP_EXTRAS
UDOS_TUI_FULL_METERS
UDOS_TUI_INVERT_HEADERS (4x)
UDOS_TUI_MAP_LEVEL
UDOS_TUI_FORCE_STATUS
UDOS_KEYMAP_PROFILE
UDOS_VIEWPORT_COLS (5x)
VIBE_STREAM_DELAY_MS
TERM
UCODE_VERSION
UDOS_AUTOMATION
UDOS_DEV_MODE
UDOS_LAUNCHER_BANNER
UDOS_PROMPT_SETUP_VIBE
VIBE_PRIMARY_PROVIDER
UDOS_OK_AUTO_FALLBACK
UDOS_OK_CLOUD_SANITY_CHECK
UDOS_DEFAULT_USER
UDOS_KEYMAP_PROFILE
OLLAMA_HOST (wizard)
MISTRAL_API_KEY (wizard)
VIRTUAL_ENV (wizard)
DISPLAY (wizard - GUI detection)
WAYLAND_DISPLAY (wizard - GUI detection)
WIZARD_APK_SIGN_KEY (wizard)
ABUILD_KEYNAME (wizard)
WIZARD_SONIC_SIGN_PUBKEY (wizard)
UDOS_CDN_BUCKET (wizard)
UDOS_CDN_ROOT (wizard)
UDOS_CDN_PREFIX (wizard)
UDOS_CDN_REGION (wizard)
UDOS_CDN_ACCESS_KEY (wizard)
UDOS_CDN_SECRET_KEY (wizard)
UDOS_CDN_PROFILE (wizard)
UDOS_ARTIFACTS_ROOT (wizard)
UDOS_TEST_RUNS_ROOT (wizard)
WIZARD_VENV_PATH (wizard)
```

### Wizard Config Variables (wizard.json)

```
host
port
debug
requests_per_minute
requests_per_hour
ai_budget_daily
ai_budget_monthly
plugin_repo_enabled
plugin_auto_update
web_proxy_enabled
ok_gateway_enabled
github_webhook_secret
github_webhook_secret_key_id
github_allowed_repo
github_default_branch
github_push_enabled
admin_api_key_id
icloud_enabled
oauth_enabled
compost_cleanup_days
compost_cleanup_dry_run
memory_root
memory_root_actual
```

