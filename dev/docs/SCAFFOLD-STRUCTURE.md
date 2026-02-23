# Understanding the `/dev/` Scaffold Structure

This guide explains the organization and purpose of each directory in the `/dev/` scaffold submodule.

---

## Overview

The `/dev/` submodule is a **framework-only scaffold** — it provides structure and templates for your development work, but contains no projects itself.

```
dev/
├── README.md           # Main guide (you are here)
├── .gitignore          # Keeps your projects private
├── wiki/               # Usage documentation
├── scripts/            # Template automation scripts
├── tools/              # Template utilities
├── examples/           # Reference implementations
├── tests/              # Template test structure
├── build/              # Build configuration templates
├── .dev/               # Your local notes (gitignored)
└── .archive/           # Your old versions (gitignored)
```

---

## Directory Guide

### `README.md`

**Purpose:** Main entry point explaining the scaffold  
**Status:** Tracked (public)  
**When to edit:** Never (it's part of the framework)

The README explains that `/dev/` is empty by design and points to `/docs/` for actual documentation.

### `.gitignore`

**Purpose:** Exclude your local projects from git  
**Status:** Tracked (public)  
**How it works:**

```gitignore
# Your projects are excluded
projects/
my-*/
custom-*/
extensions/*/
containers/*/

# Framework structure is tracked
!README.md
!wiki/
!wiki/**
!examples/
```

**Result:** Your projects in `/dev/my-extension/` stay private while the scaffold framework remains public.

### `wiki/`

**Purpose:** How-to guides for using this scaffold  
**Status:** Tracked (public)  
**Contents:**

- `README.md` — Wiki home & navigation
- `ADD-SUBMODULE.md` — Installation guide
- `DEVELOP-EXTENSION.md` — Extension development
- `DEVELOP-CONTAINER.md` — Container development
- `SCAFFOLD-STRUCTURE.md` — This file
- `API-REFERENCE.md` — uDOS API reference

**Use when:** Learning how to use the scaffold

### `scripts/`

**Purpose:** Template automation scripts you can adapt  
**Status:** Tracked (public)  
**Examples:**

```
scripts/
├── README.md
├── build.sh            # Template build script
├── test.sh             # Template test runner
├── deploy.sh           # Template deployment
└── setup.sh            # Template environment setup
```

**How to use:**

```bash
# Copy a template to your project
cp scripts/build.sh ../my-extension/
cd ../my-extension
# Edit build.sh for your needs
```

### `tools/`

**Purpose:** Template utilities for development  
**Status:** Tracked (public)  
**Examples:**

```
tools/
├── README.md
├── validate_manifest.py   # Check extension manifests
├── package_extension.py   # Create distribution archives
└── install_local.py       # Install for testing
```

**How to use:**

```bash
# Run a tool on your extension
python tools/validate_manifest.py ../my-extension/extension.json
```

### `examples/`

**Purpose:** Reference code and patterns  
**Status:** Tracked (public)  
**Structure:**

```
examples/
├── README.md
├── extensions/
│   ├── minimal/           # Bare minimum extension
│   ├── with-commands/     # Extension with commands
│   ├── with-service/      # Background service extension
│   └── with-hooks/        # Event hook examples
├── containers/
│   ├── python-app/        # Python container example
│   ├── node-service/      # Node.js service container
│   └── static-site/       # Static web server
└── patterns/
    ├── async-tasks/       # Async pattern examples
    ├── config-management/ # Configuration patterns
    └── testing/           # Testing patterns
```

**How to use:**

```bash
# Copy an example as a starting point
cp -r examples/extensions/minimal ../my-extension
cd ../my-extension
# Customize for your needs
```

### `tests/`

**Purpose:** Template test structure  
**Status:** Tracked (public)  
**Examples:**

```
tests/
├── README.md
├── test_template.py       # Test template with fixtures
├── conftest.py            # Pytest configuration
└── fixtures/
    └── sample_data.json
```

**How to use:**

```bash
# Copy test templates to your project
cp -r tests ../my-extension/
cd ../my-extension/tests
# Adapt tests for your code
```

### `build/`

**Purpose:** Build configuration templates  
**Status:** Tracked (public)  
**Examples:**

```
build/
├── README.md
├── setup.py               # Python package setup
├── pyproject.toml         # Modern Python config
├── Dockerfile             # Container template
└── .github/
    └── workflows/
        └── test.yml       # CI/CD template
```

**How to use:**

```bash
# Copy build config to your project
cp build/setup.py ../my-extension/
cp build/pyproject.toml ../my-extension/
# Customize for your package
```

### `.dev/` (Local Only)

**Purpose:** Your local notes and temporary work  
**Status:** Gitignored (private)  
**Examples:**

```
.dev/
├── session-notes.md       # Your working notes
├── debug/                 # Debug outputs
└── scratch/               # Temporary experiments
```

**Auto-created:** When you need it  
**Never committed:** Stays on your machine only

### `.archive/` (Local Only)

**Purpose:** Your historical backups  
**Status:** Gitignored (private)  
**Structure:**

```
.archive/
├── 2026-02-05-docs/       # Historical dev docs (from migration)
├── my-extension-v1/       # Your old version
└── experiments/           # Old experiments
```

**Use when:** You want to keep old versions locally but not in git

---

## Your Projects Go Here

Create your projects as subdirectories in `/dev/`:

```
dev/
├── my-extension/          # ← Your extension (gitignored)
├── my-container/          # ← Your container (gitignored)
├── custom-tool/           # ← Your tool (gitignored)
└── [framework files...]   # ← Scaffold (tracked)
```

**Key point:** The `.gitignore` automatically excludes your project directories while keeping the framework tracked.

---

## What Gets Tracked vs. Ignored

### Tracked (Public Framework)

✅ `README.md` — Scaffold guide  
✅ `wiki/` — Usage documentation  
✅ `scripts/`, `tools/`, `examples/`, `tests/`, `build/` — Templates  
✅ `.gitignore` — The exclusion rules themselves  

### Ignored (Your Private Work)

❌ `my-extension/` — Your projects  
❌ `.dev/` — Your notes  
❌ `.archive/` — Your backups  
❌ `**/.env` — Your secrets  
❌ `**/node_modules/`, `**/__pycache__/` — Dependencies  

---

## Framework Updates

When the scaffold framework is updated (new templates, wiki pages, etc.):

```bash
cd dev
git pull origin main
cd ..
git add dev
git commit -m "Update dev scaffold framework"
```

**Your projects are unaffected** — they're not part of the submodule.

---

## Contributing to the Framework

If you create useful templates or examples:

1. **Make them generic** (remove project-specific details)
2. **Add documentation** (README explaining usage)
3. **Test thoroughly** (ensure they work as templates)
4. **Submit PR** to `uDOS-dev` repository

**Don't include:**
- ❌ Your private projects
- ❌ Secrets or credentials
- ❌ Large dependencies
- ❌ Project-specific code

---

## Comparison: Framework vs. Projects

| Aspect | Framework (Tracked) | Your Projects (Ignored) |
|--------|---------------------|-------------------------|
| **Purpose** | Templates & structure | Your actual code |
| **Location** | Root `/dev/` | `/dev/my-project/` subdirs |
| **Git status** | Tracked in submodule | Gitignored |
| **Visibility** | Public | Private (local only) |
| **Updates** | Pull from upstream | You control |
| **Examples** | wiki/, scripts/, examples/ | my-extension/, my-app/ |

---

## Best Practices

✅ **Keep framework clean** — Don't modify framework files unless contributing  
✅ **Use subdirectories** — Organize your projects in `/dev/my-project/`  
✅ **Copy, don't edit** — Copy templates to your project, then customize  
✅ **Review examples** — Learn patterns from `/dev/examples/`  
✅ **Update regularly** — Pull framework updates periodically  

❌ **Don't commit projects** — They should be gitignored automatically  
❌ **Don't hardcode paths** — Use relative paths or environment variables  
❌ **Don't mix concerns** — Keep framework separate from project code  

---

## Troubleshooting

### "I accidentally committed my project"

```bash
# Remove from git but keep the files
git rm -r --cached dev/my-project
git commit -m "Remove accidentally committed project"

# Verify it's now gitignored
git status  # Should not show dev/my-project
```

### "Framework files show as modified"

You may have accidentally edited framework files:

```bash
cd dev
git status  # See what changed
git diff    # Review changes

# Reset if unintentional
git checkout .
```

### "My .gitignore isn't working"

Check if files are already tracked:

```bash
git ls-files dev/my-project
# If it shows files, they're already tracked
```

Remove from tracking:

```bash
git rm -r --cached dev/my-project
git commit -m "Stop tracking my-project"
```

---

## Next Steps

✅ **Start building:** [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md)  
✅ **Review examples:** Browse `/dev/examples/`  
✅ **Check API:** [API-REFERENCE.md](API-REFERENCE.md)  

---

**Back to:** [Wiki home](README.md)
