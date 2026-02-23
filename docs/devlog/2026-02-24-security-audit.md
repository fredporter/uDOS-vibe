# Security Audit & Remediation Plan
**Date:** 2026-02-24
**Status:** Active Investigation
**Severity:** 🔴 **CRITICAL**

---

## Executive Summary

The repository has **exposed sensitive API credentials and tokens** in the committed `.env` file. This violates the documented security model and has triggered external security alerts via email.

### Exposed Secrets Found
- **MISTRAL_API_KEY** - AI provider credential
- **WIZARD_ADMIN_TOKEN** - Admin authentication token
- **WIZARD_KEY** - Encryption key for the secrets tomb

All three should be `.gitignore`d and never committed.

---

## Current Architecture vs. Reality

### ✅ **DESIGNED CORRECTLY** (Per ENV-STRUCTURE-V1.1.0)

The documented security model is sound:

| Secret Type | Intended Storage | Encryption | Access |
|---|---|---|---|
| **Local Identity** (name, location, timezone) | `.env` (plaintext) | ❌ No | Local only |
| **API Keys & Tokens** | `wizard/secrets.tomb` | ✅ **Fernet** | WIZARD_KEY unlock |
| **WIZARD_KEY** | `.env` (unencrypted UUID) | ❌ No | .gitignore |
| **WIZARD_ADMIN_TOKEN** | `wizard/secrets.tomb` | ✅ **Fernet** | Encrypted storage |

### ❌ **BROKEN IN PRACTICE**

Currently, the `.env` file in git contains:
```env
MISTRAL_API_KEY=IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe           # ← EXPOSED (should be in secrets.tomb)
WIZARD_ADMIN_TOKEN=RyYBc1RZCLsIgWd29zl5-zMXE17jMwQJe...   # ← EXPOSED (should be in secrets.tomb)
WIZARD_KEY=kJAtsfYmfYpY3Nf8EfcD7DvvMi9zhAPu0NLRS3X3LYN... # ← EXPOSED (should be .gitignore)
```

---

## Root Cause Analysis

### Why This Happened

1. **`.env` was never meant to be committed** – but it was (possibly for convenience during development)
2. **No pre-commit hook** to prevent secrets commits
3. **No CI validation** checking for secret patterns in .env before merging
4. **Development convenience override** – simpler to use .env than manage secrets.tomb locally

### Why This Is Dangerous

- ✅ `.env` is in `.gitignore` (correct policy)
- ❌ **But the file was already committed** – history is in git
- ❌ **GitHub Actions workflows** may also have exposure risk
- ❌ **External integrations** (Mistral, GitHub) could be accessed with exposed keys

---

## Immediate Actions Required

### 1. **Revoke All Exposed Secrets** (URGENT)
- [ ] **Mistral API:** Revoke `IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe` at console.mistral.ai
- [ ] **Wizard Admin Token:** Reset via wizard/tools/secret_store_cli.py or Wizard dashboard
- [ ] **WIZARD_KEY:** Regenerate and distribute to team (only local machines)

### 2. **Remove Secrets from Git History**
```bash
# Option A: Use git-filter-repo (recommended, rewrites history)
brew install git-filter-repo
git filter-repo --invert-paths --path .env  # Remove all .env from history
git filter-repo --replace-text <(echo 'IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe==>REVOKED==>') # Remove value

# Option B: Force-push (if no downstream dependencies)
# git push origin --force --all  # ⚠️ Breaks for collaborators

# Option C: Accept compromise, mark as void, plan rotation
# (if git-filter-repo is too risky for your workflow)
```

### 3. **Create `.env.example` Template**
```env
# .env.example — Copy to .env and fill in your values
# This file should be safe to commit (no secrets)

# ── REQUIRED: Core paths ────────────────────────────────────
UDOS_ROOT=/path/to/uDOS-vibe
VAULT_ROOT=${UDOS_ROOT}/memory/vault
VAULT_MD_ROOT=${UDOS_ROOT}/memory/vault

# ── REQUIRED: Identity ───────────────────────────────────────
USER_NAME=YourName

# ── REQUIRED: Locale ─────────────────────────────────────────
UDOS_TIMEZONE=UTC
UDOS_LOCATION=grid-code
UDOS_LOCATION_NAME=Greenwich
UDOS_GRID_ID=

# ── AI Provider ──────────────────────────────────────────────
# DO NOT PUT ACTUAL KEYS HERE!
# Set only in Wizard dashboard or wizard/secrets.tomb via setup story
MISTRAL_API_KEY=

# ── Wizard Server ────────────────────────────────────────────
# DO NOT PUT ACTUAL TOKENS HERE!
# Set via wizard/tools/secret_store_cli.py or Wizard dashboard
WIZARD_ADMIN_TOKEN=
WIZARD_KEY=

# ── Rest of config (non-sensitive only) ──────────────────────
OS_TYPE=mac
UDOS_AUTOMATION=0
UDOS_DEV_MODE=0
# ...
```

### 4. **CI Guards: Prevent Future Commits**
Create `.github/workflows/secrets-check.yml`:
```yaml
name: Secrets Check
on: [push, pull_request]
jobs:
  detect-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run TruffleHog (secret scanner)
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      - name: Check .env structure
        run: |
          if [ -f .env ]; then
            # Reject API keys in .env
            if grep -iE '(MISTRAL|ANTHROPIC|OPENAI|GITHUB|AWS).*API.*KEY|TOKEN|SECRET' .env | grep -v '^#'; then
              echo "❌ ERROR: API keys/tokens found in .env"
              echo "Move them to wizard/secrets.tomb via Wizard dashboard"
              exit 1
            fi
          fi
```

---

## Long-Term Architecture Fix

### Recommended Approach: **Wizard-First Secrets Management**

**Current Design is Correct, but Under-enforced:**

```
┌─────────────────────────────────────────────────────┐
│  Development / Local Setup                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  .env (committed)                                   │
│  ├─ USER_NAME = "Fredrick"                          │
│  ├─ UDOS_LOCATION = "grid-code"                     │
│  ├─ OS_TYPE = "mac"                                 │
│  ├─ WIZARD_KEY = <64-char hex> (generated locally)  │
│  └─ (NO API KEYS)                                   │
│                                                     │
│  .env.local (NOT committed, per team agreement)     │
│  └─ CI/deployment overrides only if needed          │
│                                                     │
└─────────────────────────────────────────────────────┘
          ↓ (WIZARD_KEY unlocks)
┌─────────────────────────────────────────────────────┐
│  wizard/secrets.tomb (encrypted blob)               │
│  .gitignore protected                               │
├─────────────────────────────────────────────────────┤
│  Encrypted Fernet payload:                          │
│  ├─ mistral-api-key = "IUvYK..."                    │
│  ├─ wizard-admin-token = "RyYBc..."                 │
│  ├─ github-token = "ghp_..."                        │
│  ├─ anthropic-api-key = "sk-..."                    │
│  └─ ... other provider credentials                  │
│                                                     │
└─────────────────────────────────────────────────────┘
          ↓ (requires admin token + WIZARD_KEY)
┌─────────────────────────────────────────────────────┐
│  Wizard Dashboard / API                             │
│  http://localhost:8765/dashboard                    │
├─────────────────────────────────────────────────────┤
│  Manage secrets GUI:                                │
│  ├─ Rotate keys                                     │
│  ├─ Add/remove integrations                         │
│  ├─ Inspect (masked)                                │
│  └─ Export (encrypted to temp file)                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Migration Steps:**

1. ✅ **Setup Story** (already exists) – generates `.env` + `secrets.tomb`
2. ✅ **Wizard Dashboard** (already exists) – manage stored secrets
3. ✅ **Secret Store CLI** (already exists) – rotate keys safely
4. ❌ **Documentation** – Users still putting keys in `.env`
5. ❌ **CI Validation** – No gate to prevent accidents

---

## GitHub Actions Integration Issues

### Current State (from wizard_config.py)
```python
github_webhook_secret: Optional[str] = None
github_webhook_secret_key_id: Optional[str] = None
github_allowed_repo: str = "fredporter/uDOS-dev"
github_default_branch: str = "main"
github_push_enabled: bool = False
```

### Problems Identified
1. **Multiple GitHub integrations** scattered across codebase (tui, telemetry, update_notifier)
2. **No consolidated webhook handler** for CI workflow events
3. **GITHUB_TOKEN** sometimes requested from env, sometimes from secrets.tomb
4. **Push capability disabled** but structure left in code (maintenance debt)

### Recommended Fix: Consolidate GitHub Integration

Create `wizard/services/github_integration.py`:
```python
from typing import Optional
from wizard.security.key_store import get_wizard_key, set_wizard_key

class GitHubIntegration:
    """Consolidated GitHub integration (webhook, releases, auth)."""

    @staticmethod
    def get_token() -> Optional[str]:
        """Retrieve GitHub token from secrets.tomb."""
        return get_wizard_key("github-token")

    @staticmethod
    def get_webhook_secret() -> Optional[str]:
        """Retrieve webhook secret for signature verification."""
        return get_wizard_key("github-webhook-secret")

    @staticmethod
    def verify_webhook(payload: str, signature: str) -> bool:
        """Verify GitHub webhook X-Hub-Signature-256."""
        secret = self.get_webhook_secret()
        if not secret:
            return False
        # HMAC-SHA256 verify
        ...

    @classmethod
    def setup_from_wizard_config(cls) -> None:
        """Initialize from wizard.json settings."""
        config = load_wizard_config_data()
        if webhook_secret := config.get("github_webhook_secret"):
            set_wizard_key("github-webhook-secret", webhook_secret)
```

**Then unify all callers:**
```python
# Before: scattered, fragile
token = os.getenv("GITHUB_TOKEN")

# After: consistent, secure
token = GitHubIntegration.get_token()
```

---

## Action Priority & Timeline

### 🔴 **CRITICAL (Today)**
- [ ] Revoke `MISTRAL_API_KEY` at console.mistral.ai
- [ ] Reset `WIZARD_ADMIN_TOKEN` via Wizard dashboard
- [ ] Regenerate `WIZARD_KEY` locally (docs: `wizard/tools/reset_secrets_tomb.py`)
- [ ] Remove `.env` from git history (use git-filter-repo or accept compromise)
- [ ] Create `.env.example` template
- [ ] Add to `.gitignore` if not already present (verify)

### 🟡 **HIGH (This Week)**
- [ ] Set up secrets detection in CI (TruffleHog + .env structure check)
- [ ] Update docs/INSTALLATION.md with "Never put secrets in .env"
- [ ] Create setup guide: wizardos/howto/SETUP-SECRETS.md
- [ ] Add pre-commit hook (optional_hooks/detect-secrets or similar)

### 🟢 **MEDIUM (This Sprint)**
- [ ] Consolidate GitHub integration into `wizard/services/github_integration.py`
- [ ] Migrate vibe/cli code to use GitHubIntegration
- [ ] Test webhook signature verification
- [ ] Simplify wizard.json – remove unused `github_push_enabled` if truly unused

### 🔵 **LOW (Future)**
- [ ] Add OS keychain integration (macOS Keychain, Windows Credential Manager)
- [ ] Implement secret rotation schedule
- [ ] Add audit log for secret access

---

## Verification Checklist

Once completed, verify:

- [ ] `.env` file contains no API keys, tokens, or secrets
- [ ] All API credentials exist in `wizard/secrets.tomb`
- [ ] `WIZARD_KEY` is unique per environment (not in git)
- [ ] `WIZARD_ADMIN_TOKEN` is cryptographically random
- [ ] CI prevents commits with exposed secret patterns
- [ ] Team docs mention "never put secrets in .env"
- [ ] GitHub webhook integration uses secrets.tomb path
- [ ] All revealed secrets are rotated/revoked

---

## References

- [ENV-STRUCTURE-V1.1.0.md](../specs/ENV-STRUCTURE-V1.1.0.md) – Correct design
- [wizard/security/key_store.py](../../wizard/security/key_store.py) – Encryption layer
- [wizard/services/secret_store.py](../../wizard/services/secret_store.py) – Tomb implementation
- [wizard/tools/secret_store_cli.py](../../wizard/tools/secret_store_cli.py) – CLI tool
- [wizard/tools/reset_secrets_tomb.py](../../wizard/tools/reset_secrets_tomb.py) – Reset procedure

---

## Team Communication

**Required Message to Share:**

> ⚠️ **SECURITY INCIDENT:** API keys were exposed in the committed `.env` file. We are immediately revoking all exposed credentials and implementing detection gates.
>
> **For your local setup:**
> 1. Delete `.env` and run SETUP story to regenerate it
> 2. Never put API keys in `.env` — they belong in the Wizard dashboard
> 3. CI will now reject commits containing secrets
>
> **More details:** docs/devlog/2026-02-24-security-audit.md

