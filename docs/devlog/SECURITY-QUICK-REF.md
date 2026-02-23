# Security Incident — Quick Reference Card

## Status: 🔴 CRITICAL — API Keys Exposed in Git

**Date Discovered:** 2026-02-24
**Exposed Secrets:** 3 (MISTRAL_API_KEY, WIZARD_ADMIN_TOKEN, WIZARD_KEY)
**Location:** `.env` file (committed to git)

---

## IMMEDIATE TO-DO (Do NOW)

```bash
# 1. Rotate exposed credentials
#    • Mistral: https://console.mistral.ai (revoke + create new)
#    • GitHub: https://github.com/settings/tokens
#    • Any other exposed keys

# 2. Remove .env from git history (coordinate with team)
git filter-repo --invert-paths --path .env
git push origin --force --all --prune

# 3. Reset local secrets
rm .env
cp .env.example .env
python uDOS.py          # Choose SETUP
WIZARD start            # Add new API keys via dashboard
```

**Estimated Time:** 15-30 minutes

---

## What Was Exposed

| Secret | Status | Rotation Method |
|--------|--------|-----------------|
| `MISTRAL_API_KEY` | 🔴 CRITICAL | Revoke at console.mistral.ai, create new |
| `WIZARD_ADMIN_TOKEN` | 🟡 HIGH | Reset via `wizard/tools/reset_secrets_tomb.py` |
| `WIZARD_KEY` | 🟡 HIGH | Regenerate via SETUP story |

---

## What We Fixed

### ✅ CI Protection (Live)
- **File:** `.github/workflows/secrets-check.yml`
- **Does:** Scans every push/PR for exposed secrets
- **Blocks:** Commits with API keys in `.env`

### ✅ Documentation (Live)
1. **Incident Analysis:** `docs/devlog/2026-02-24-security-audit.md`
2. **Incident Summary:** `docs/devlog/2026-02-24-incident-summary.md`
3. **How-To Guide:** `docs/howto/SETUP-SECRETS.md`

### ✅ Template Warnings (Live)
- **File:** `.env.example`
- **Updates:** Clear 🔐 warnings about API keys
- **Links:** References to documentation

### ✅ Architecture Verified
- `.env` is in `.gitignore` ✅
- `secrets.tomb` is in `.gitignore` ✅
- Encryption is Fernet (AES-128) ✅
- Design is correct, enforcement was missing ✅

---

## GitHub Actions Integration

### Current Issues
- GitHub tokens scattered across codebase
- No consolidated handler
- Multiple access patterns (env var vs secrets.tomb)

### Recommendation
**Priority:** Medium (not urgent)
**Solution:** Create unified `GitHubIntegration` class
**Timeline:** Next sprint or when webhook handler needed

---

## Key Files Changed

| File | Change | Reason |
|------|--------|--------|
| `.env.example` | Added security warnings | Prevent future accidents |
| `.github/workflows/secrets-check.yml` | NEW | Block commits with secrets |
| `docs/devlog/2026-02-24-security-audit.md` | NEW | Full incident analysis |
| `docs/devlog/2026-02-24-incident-summary.md` | NEW | Quick reference + actions |
| `docs/howto/SETUP-SECRETS.md` | NEW | Practical how-to guide |

---

## Verification Checklist

After implementing fixes:

- [ ] All three exposed keys are rotated at provider
- [ ] MISTRAL_API_KEY is new and in secrets.tomb (not `.env`)
- [ ] WIZARD_ADMIN_TOKEN is regenerated
- [ ] WIZARD_KEY is unique to your machine
- [ ] `.env` is removed from git history (or team agrees to accept it)
- [ ] Local `.env` is regenerated via SETUP
- [ ] CI workflow is passing (green check on PR)
- [ ] TruffleHog scan finds no secrets
- [ ] Team is notified and knows to read docs/howto/SETUP-SECRETS.md

---

## Team Communication

Share this message:

```
🔒 SECURITY INCIDENT: API Credentials Exposed

Exposed keys have been detected in the committed .env file.
We are immediately rotating all credentials and implementing detection gates.

✅ For your local setup:
   1. rm .env
   2. cp .env.example .env
   3. python uDOS.py (SETUP)
   4. WIZARD start → Add API keys via dashboard

⛔ Never put API keys in .env!
   They belong in wizard/secrets.tomb (encrypted).

📖 Detailed info:
   • docs/devlog/2026-02-24-security-audit.md (full analysis)
   • docs/howto/SETUP-SECRETS.md (how to do this right)
```

---

## References

- **Design Spec:** [ENV-STRUCTURE-V1.1.0.md](../specs/ENV-STRUCTURE-V1.1.0.md)
- **Security Tools:** `wizard/tools/` (check_secrets_tomb.py, reset_secrets_tomb.py)
- **Encryption:** Fernet (cryptography library, AES-128)
- **CI Config:** `.github/workflows/secrets-check.yml`

---

## Questions?

**Q: Do I need to do anything if I don't have access to the repo?**
A: Just pull the latest code after the incident is resolved. Your local `.env` won't be affected.

**Q: Will CI block my normal PRs?**
A: No, only if you accidentally add secrets. `.env.example` with no keys is fine.

**Q: What about GitHub Actions secrets?**
A: Use GitHub's built-in secrets (Settings > Secrets > New repo secret). Different system.

**Q: How do I test that secrets rotation worked?**
A: After adding new key to Wizard: `vibe ask "test"`

---

**Last Updated:** 2026-02-24
**Status:** Active — Awaiting Implementation
**Contact:** Team Lead / Security Officer

