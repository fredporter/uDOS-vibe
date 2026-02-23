# Security Incident Response Summary
**Date:** 2026-02-24
**Status:** Active Investigation & Remediation
**Severity Level:** 🔴 CRITICAL

---

## What Happened

You received an email alert that **API credentials were exposed in git**. Investigation confirms:

### ✅ Confirmed Exposures in `.env`
Three sensitive secrets were visible in the committed `.env` file:
1. **MISTRAL_API_KEY** = `IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe`
2. **WIZARD_ADMIN_TOKEN** = `RyYBc1RZCLsIgWd29zl5-zMXE17jMwQJeqqU8aBeLDH5-BBdX28sFu3D5rSlThR7`
3. **WIZARD_KEY** = `kJAtsfYmfYpY3Nf8EfcD7DvvMi9zhAPu0NLRS3X3LYN321xnoM-HPwlwCJuyr25T`

### ✅ Good News: The Architecture is Correct
- Your documented security model (ENV-STRUCTURE-V1.1.0) is **sound**
- `.env` and `secrets.tomb` **are** properly in `.gitignore`
- Fernet encryption for `secrets.tomb` is **correctly implemented**

### ❌ The Problem: Policy Wasn't Enforced
- The `.env` file was committed anyway
- No pre-commit hook or CI gate to prevent this
- No explicit guidance to developers about what shouldn't go in `.env`

---

## Immediate Actions (Do These Today)

### 1️⃣ Revoke All Exposed Credentials

**Mistral API Key:**
- 🔗 Go to: https://console.mistral.ai
- Delete the exposed key `IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe`
- Generate a new API key
- Add to Wizard via dashboard (Settings > Integrations > Mistral)

**Wizard Admin Token & WIZARD_KEY:**
- These are local-only encryption keys
- Safe to regenerate via: `uv run wizard/tools/reset_secrets_tomb.py`
- Or via Wizard dashboard: Settings > Secret Store > Repair

### 2️⃣ Remove `.env` from Git History

Choose one approach:

**Option A: `git-filter-repo` (Recommended, clean history)**
```bash
# Install the tool
brew install git-filter-repo

# Remove ALL .env files from history
git filter-repo --invert-paths --path .env

# Remove specific exposed values
git filter-repo --replace-text <(echo 'IUvYKyQcVs6Rdcflb1fE9XvfhhGfkoPe==>REVOKED==>')

# Force push (⚠️ This breaks repos for other developers - coordinate!)
git push origin --force --all --prune
```

**Option B: Accept Compromise (Simpler, marks commit as void)**
- Document in CHANGELOG that the key was rotated
- Create a new commit showing the rotation
- Accept that history contains exposed keys but highlight rotation in doc

### 3️⃣ Reset Your Local `.env`

```bash
# Back up current .env (just in case)
cp .env .env.backup

# Delete it
rm .env

# Restore from example
cp .env.example .env

# Run SETUP to regenerate credentials
python uDOS.py
# Choose: SETUP

# Start Wizard and add API keys via dashboard
WIZARD start
# Visit: http://localhost:8765/dashboard
# Settings > Integrations > Add Secret
```

---

## Preventive Measures (This Week)

### ✅ CI Workflow Added
**New file:** `.github/workflows/secrets-check.yml`
- Runs on every push and PR
- Uses TruffleHog to detect exposed secrets
- Checks `.env` structure for forbidden patterns
- Blocks commits with exposed API keys

### ✅ Documentation Updated
**New files created:**
1. **[docs/howto/SETUP-SECRETS.md](../howto/SETUP-SECRETS.md)** — Practical guide for managing secrets
   - How to add API keys safely
   - Step-by-step via Wizard dashboard
   - Troubleshooting guide
   - GitHub integration consolidation plan

2. **[docs/devlog/2026-02-24-security-audit.md](../devlog/2026-02-24-security-audit.md)** — Full incident analysis
   - Root cause analysis
   - Architecture review
   - Detailed action plan
   - Timeline and priorities
   - References to existing tools

### ✅ Template Improved
**Updated file:** `.env.example`
- Added prominent security warnings
- Marked all API key fields with 🔐
- Clear instructions: "DO NOT PUT YOUR ACTUAL KEY HERE"
- Reference to Wizard dashboard setup steps
- Link to detailed security docs

### ✅ `.gitignore` Verified
- `.env` is properly ignored ✅
- `*.tomb` is properly ignored ✅
- `memory/private/` is properly ignored ✅
- No configuration needed

---

## Architecture Summary

Your security design **separates concerns correctly**:

```
┌─────────────────────┬──────────────┬─────────────┐
│   Storage Layer     │ Encryption   │ Committed?  │
├─────────────────────┼──────────────┼─────────────┤
│ .env (IDENTITY)     │ ❌ Plaintext │ ❌ Git only │
│ • USER_NAME         │              │ .env.ex...  │
│ • TIMEZONE          │              │             │
│ • LOCATION          │              │             │
├─────────────────────┼──────────────┼─────────────┤
│ .env (KEYS)         │ ❌ None      │ ❌ NEVER    │
│ • WIZARD_KEY        │ (just unlock │ (only local)│
│ • WIZARD_ADMIN_TOKEN│  key)        │             │
├─────────────────────┼──────────────┼─────────────┤
│ secrets.tomb        │ ✅ Fernet    │ ❌ NEVER    │
│ • API keys          │ (AES-128)    │ (encrypted) │
│ • OAuth tokens      │              │             │
│ • Cloud creds       │              │             │
└─────────────────────┴──────────────┴─────────────┘
```

---

## Verification Checklist

After implementing the above, verify:

- [ ] All exposed keys are rotated/revoked at provider
- [ ] `.env` is removed from git history (or marked as void with documentation)
- [ ] Local `.env` is regenerated via SETUP story
- [ ] CI workflow `secrets-check.yml` is running on PRs
- [ ] No secrets fail TruffleHog scan
- [ ] `.env.example` is updated with security warnings
- [ ] Team is notified of changes via doc link
- [ ] New team members know to read docs/howto/SETUP-SECRETS.md

---

## Ongoing Maintenance

### Monthly
- Review CI logs for secret detection hits
- Rotate critical API keys (Mistral, GitHub tokens)

### Quarterly
- Update security documentation
- Review access logs (when audit logging added)
- Test disaster recovery (re-running SETUP)

### As Needed
- Revoke compromised keys immediately
- Re-run git-filter-repo if new exposures found
- Add new secret patterns to CI detection

---

## GitHub Actions Integration Status

### Current State
GitHub integrations are scattered:
- `wizard/services/wizard_config.py` — Webhook config
- `vibe/cli/update_notifier/` — Release checking
- `vibe/cli/textual_ui/app.py` — Token teleport
- `.github/workflows/` — CI workflows

### Recommended Consolidation
Create `wizard/services/github_integration.py`:
```python
class GitHubIntegration:
    """Unified GitHub integration."""
    @staticmethod
    def get_token() -> str: ...
    @staticmethod
    def get_webhook_secret() -> str: ...
    @staticmethod
    def verify_webhook(payload, signature) -> bool: ...
```

**Priority:** Medium (not urgent, but improves maintainability)
**Timeline:** Next sprint or as part of webhook handler implementation

---

## Questions & Answers

**Q: Can I recover the .env commit from git history?**
A: Yes, but it exposes keys. Better to rotate them and use `git-filter-repo` to clean history.

**Q: Do I need to regenerate WIZARD_KEY?**
A: Only if you want fresh encryption. The compromised keys (Mistral, admin token) are the priority.

**Q: What if I use CI secrets (GitHub Actions secrets)?**
A: Unrelated to this incident. CI-level secrets are handled separately via GitHub's encrypted storage.

**Q: How do I add an API key to a GitHub workflow?**
A: Use GitHub Actions secrets (Settings > Secrets > New repository secret), NOT `.env`.

**Q: Should I create `.env.local` instead?**
A: Yes, `.env.local` is ignored and can override `.env.example` locally. But still never put secrets there.

---

## Links & References

- 📖 [ENV-STRUCTURE-V1.1.0.md](../specs/ENV-STRUCTURE-V1.1.0.md) — Correct security design
- 📖 [SETUP-SECRETS.md](../howto/SETUP-SECRETS.md) — Practical how-to guide
- 🔧 [wizard/tools/](../../wizard/tools/) — Secret management tools
  - `check_secrets_tomb.py` — Diagnostic tool
  - `reset_secrets_tomb.py` — Reset procedure
  - `secret_store_cli.py` — CLI management
- 🔐 [wizard/security/key_store.py](../../wizard/security/key_store.py) — Encryption layer
- 🔐 [wizard/services/secret_store.py](../../wizard/services/secret_store.py) — Tomb implementation

---

## Team Communication Template

Share this with your team:

> ⚠️ **INCIDENT: API Keys Exposed in Git**
>
> **What:** Three API credentials were visible in the committed `.env` file.
> **When:** Discovered 2026-02-24
> **Action:** All keys are being rotated. Repository will be cleaned up.
>
> **For Your Local Setup:**
> 1. Delete your `.env` file: `rm .env`
> 2. Restore from template: `cp .env.example .env`
> 3. Re-run SETUP: `python uDOS.py` (pick SETUP)
> 4. Add API keys via Wizard: `WIZARD start` then Settings > Integrations
>
> **Why This Happened:**
> - `.env` should never contain API keys (design says only local identity)
> - No pre-commit hook to prevent accidental commits
> - No CI validation of secrets
>
> **What We Fixed:**
> - CI workflow now scans for exposed secrets
> - `.env.example` updated with clear warnings
> - New guide: docs/howto/SETUP-SECRETS.md
>
> **More Details:**
> - Full analysis: docs/devlog/2026-02-24-security-audit.md
> - How-to guide: docs/howto/SETUP-SECRETS.md
> - Secret management: wizard/tools/

