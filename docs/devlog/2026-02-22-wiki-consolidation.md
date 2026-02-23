# Wiki Consolidation - 2026-02-22

## Summary

Cleaned up wiki directory by removing redundant files, fixing broken links, updating version references, and aligning with Vibe-first architecture.

## Changes Made

### 1. Removed Redundant Files (3 files)

**Deleted:**
- `wiki/README.md` - Redundant with Home.md (Home.md is canonical wiki landing page)
- `wiki/CONTRIBUTING.md` - Outdated, deferred to root CONTRIBUTING.md (Mistral canonical)
- `wiki/Contributors.md` - Duplicate contributor guidance, Credits.md kept

**Rationale:** Root CONTRIBUTING.md is canonical from Mistral. Wiki-specific old uDOS CONTRIBUTING.md had wrong repo (fredporter/uDOS), wrong install method (venv/pip instead of uv), and outdated guidance.

### 2. Updated Home.md

**Changes:**
- Updated version: v1.4.4 → v1.4.4+
- Removed dead links to non-existent files:
  - `../docs/WORKFLOW-TASK-COMPLETE-INDEX.md`
  - `../docs/releases/v1.4.4-release-notes.md`
  - `../docs/WORKFLOW-TASK-IMPLEMENTATION-GUIDE.md`
- Removed old issue tracker links (fredporter/uDOS)
- Updated contributing links to point to root CONTRIBUTING.md
- Streamlined "Canonical Specs" section

### 3. Updated Navigation (_Sidebar.md, _Footer.md)

**_Sidebar.md:**
- Removed references to deleted files (CONTRIBUTING.md, Contributors.md)
- Removed broken external links (issue templates)
- Added Beacon.md to navigation
- Updated docs links to current state

**_Footer.md:**
- Changed from issues link to repo link
- Updated to mistralai/mistral-vibe repository

### 4. Version Consistency (8 files updated)

Updated all wiki files from v1.4.3 → v1.4.4+:
- Dev-Tools.md
- Core.md
- VISION.md
- Self-Healing.md
- BEACON.md
- Credits.md
- Wizard.md
- ARCHITECTURE.md

Updated "Last Updated" dates to 2026-02-22 across all files.

### 5. Development Workflow Updates

**Dev-Tools.md:**
- Changed from venv/pip → uv workflow
- Updated install commands: `uv sync`, `uv run pytest`
- Updated architecture description to reflect Vibe-first (vibe/, core/, wizard/, sonic/)
- Updated style guide reference: Style-Guide.md → AGENTS.md

### 6. Content Corrections

**ARCHITECTURE.md:**
- Updated versioning section: removed v1.4.3 release tracking reference
- Added note about command infrastructure accessible via Vibe CLI and shell

**BEACON.md:**
- Removed specific v1.4.3 release scope language
- Generic "not part of current baseline" language

**Wizard.md:**
- Removed specific v1.4.3 baseline references

## Final Wiki Structure

```
wiki/
├── Home.md                         # ✅ Wiki landing page
├── Installation.md                 # ✅ User installation guide
├── ARCHITECTURE.md                 # ✅ System architecture
├── Core.md                         # ✅ Core component docs
├── Wizard.md                       # ✅ Wizard component docs
├── BEACON.md                       # ✅ Beacon portal concept
├── TypeScript-Runtime.md           # ✅ TS runtime reference
├── TUI-Z-Layer-and-TOYBOX.md      # ✅ Spatial data & theming
├── Self-Healing.md                 # ✅ Self-healing systems
├── Dev-Tools.md                    # ✅ Developer tools (updated to uv)
├── VISION.md                       # ✅ Project vision
├── Credits.md                      # ✅ Credits & inspiration
├── _Sidebar.md                     # ✅ Wiki navigation
└── _Footer.md                      # ✅ Wiki footer

Total: 14 files (was 17)
```

## Impact

- ✅ Removed 3 redundant/outdated files
- ✅ Fixed all broken internal links
- ✅ Consistent v1.4.4+ version references
- ✅ Updated to uv workflow (modern Python packaging)
- ✅ Aligned with Vibe-first architecture
- ✅ Correct repository references (mistralai/mistral-vibe)
- ✅ Streamlined navigation

## Cross-References

- [docs/devlog/2026-02-22-docs-consolidation.md](2026-02-22-docs-consolidation.md) - Documentation consolidation
- [AGENTS.md](../../AGENTS.md) - Documentation guidelines
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Canonical contributing guide
