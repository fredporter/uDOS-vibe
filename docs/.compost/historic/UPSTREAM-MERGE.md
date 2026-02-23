# Merging Vibe Upstream
## Handling Future Vibe Releases

When Mistral releases a new version of Vibe, merging is straightforward because of the addon model.

---

## Current State

```
pyproject.toml:
  mistralai==1.9.11    ← Pinned (vibe's direct dep)
  mcp>=1.14.0          ← Flexible (we use MCP in Phase B)

vibe/:
  version = "2.2.1"    ← Whatever upstream is at

Our code:
  vibe/core/tools/ucode/      ← Addon (never modified by upstream)
  vibe/core/skills/ucode/     ← Addon (never modified by upstream)
  core/, wizard/              ← Isolated (never touched by vibe)
  .vibe/config.toml           ← Integration point (we control)
```

---

## Merge Procedure (Safe & Fast)

### 1. Fetch & Check

```bash
cd /Users/fredbook/Code/uDOS-vibe

git remote add upstream https://github.com/mistralai/mistral-vibe.git
git fetch upstream main

# See what changed in vibe/
git diff upstream/main -- vibe/ | head -50

# Should see lots of upstream changes, but NOT vibe/core/tools/ucode/ or vibe/core/skills/ucode/
# (those are ours)
```

### 2. Merge (Usually Conflict-Free)

```bash
# Merge upstream
git merge upstream/main

# If conflicts: They'll be in vibe/* files only (which we can resolve)
# Our addon code (vibe/core/tools/ucode, vibe/core/skills/ucode) won't conflict
```

### 3. Validate

```bash
# Re-install dependencies (vibe's versions may have updated)
pip install -e .[udos-wizard]

# Quick check: Are our tools still discoverable?
python -c "
from vibe.core.tools.tool_manager import ToolManager
tm = ToolManager()
tools = tm.resolve_local_tools_dir('vibe/core/tools/ucode')
print(f'✅ Found {len(tools)} uDOS tools' if tools else '❌ No tools found')
"

# Quick check: Are our skills still discoverable?
python -c "
from vibe.core.skills.skill_manager import SkillManager
sm = SkillManager()
skills = sm.discover_skills('vibe/core/skills/ucode')
print(f'✅ Found {len(skills)} uDOS skills' if skills else '❌ No skills found')
"

# Run a quick vibe test
vibe -p "What tools do you have?" --enabled-tools "ucode*"
```

### 4. Commit

```bash
git add -A
git commit -m "Merge Mistral Vibe upstream — $(git describe --tags upstream/main)"
```

---

## What Could Break? (Very Low Risk)

| Change | Likelihood | Impact | Fix |
|--------|------------|--------|-----|
| BaseTool.run() signature | 🟢 Low | Medium | Update _base.py signature, re-test |
| ToolManager API | 🟢 Low | Medium | Update tool discovery setup if needed |
| Skill markdown format | 🟡 Very Low | Low | Minor markdown changes to .md files |
| New vibe dependencies | 🟢 Low | Low | `pip install` picks them up automatically |
| mistralai client API | 🟢 Low | Low | Vibe handles, we just call mistralai |

**Why so safe?**
- Vibe's APIs (BaseTool, ToolManager, SkillManager) are **stable** (Apache 2.0, production)
- Vibe updates are tested by Mistral team before release
- We're using public APIs, not monkey-patching internals
- Core vibe tests verify BaseTool API compatibility

---

## Version Pinning Strategy

### Current (Conservative)

```toml
mistralai==1.9.11     # Pinned to exact version
mcp>=1.14.0           # Flexible (stable protocol)
```

**Pros:**
- Reproducible builds
- Won't break unexpectedly
- Controlled integration testing

**Cons:**
- Miss security fixes in mistralai
- Manual updates needed

### Alternative (Flexible, With Testing)

```toml
mistralai>=1.9.0,<3.0.0   # Allow minor/patch updates
mcp>=1.14.0                # Allow updates
```

**Pros:**
- Auto-pick up security patches
- Simpler maintenance

**Cons:**
- Need CI tests to catch breaks
- Occasional surprises

### Recommendation

**Keep current (pinned)** for stability. When vibe releases:

1. Test the upgrade in a feature branch
2. Merge vibe, run validation checks above
3. If all pass → merge to main
4. If tests fail → check what changed in vibe/core/tools/base.py, update our tools accordingly

---

## When to Update?

| Trigger | Action |
|---------|--------|
| **vibe minor release** (2.2 → 2.3) | Test & merge at your pace (within a month) |
| **vibe security patch** (2.2.0 → 2.2.1) | Merge immediately after validation |
| **mistralai security fix** | Update within a week if applicable |
| **mcp new version** | Update if Phase B is active, test first |

---

## Automated Checks (Optional)

If you want to automate the merge validation, here's a simple GitHub Actions workflow:

```yaml
# .github/workflows/merge-upstream.yml
name: Merge Vibe Upstream

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 9 * * MON'  # Weekly on Mondays

jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Fetch upstream
        run: git fetch https://github.com/mistralai/mistral-vibe.git main:upstream

      - name: Check for conflicts
        run: |
          if git merge-base --is-ancestor upstream HEAD; then
            echo "✅ Already up-to-date"
            exit 0
          fi
          git merge --no-commit --no-ff upstream || {
            echo "❌ Merge conflicts detected"
            git merge --abort
            exit 1
          }
          git merge --abort
          echo "✅ Merge possible (no conflicts)"

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Validate addon discovery
        run: |
          pip install -e .[udos-wizard]
          python -c "
          from vibe.core.tools.tool_manager import ToolManager
          tm = ToolManager()
          tools = tm.resolve_local_tools_dir('vibe/core/tools/ucode')
          assert tools, 'No tools discovered'
          print(f'✅ Found {len(tools)} tools')
          "

      - name: Create PR
        if: success()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.pulls.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Merge Mistral Vibe Upstream',
              head: 'merge-vibe-upstream',
              base: 'main',
              body: 'Automated merge of Mistral Vibe upstream. All validation checks passed.'
            })
```

---

## Real Example: What Happens

### Before Merge

```
uDOS-vibe/
├── vibe/                              ← v2.2.1 from Mistral
│   ├── core/tools/
│   │   ├── ucode/
│   │   │   ├── _base.py              ← OUR code
│   │   │   ├── system.py             ← OUR code
│   │   │   └── ...
│   │   └── ...vibe built-ins
│   └── ...vibe v2.2.1
├── core/                              ← uDOS (untouched)
└── .vibe/config.toml                  ← OUR integration
```

### git merge upstream/main happens

```
Mistral releases Vibe 2.3.0 with:
  - Updated mistralai client (1.9.11 → 1.10.0)
  - New ToolManager features
  - Better skill support
  - Security patches

What changes:
  ✅ vibe/cli/
  ✅ vibe/core/llm/
  ✅ vibe/core/tools/base.py       ← Might need validation
  ✅ vibe/core/skills/base.py      ← Might need validation
  ❌ vibe/core/tools/ucode/        ← NOT TOUCHED (our addon)
  ❌ vibe/core/skills/ucode/       ← NOT TOUCHED (our addon)
  ❌ core/                          ← NOT TOUCHED (isolated)
  ❌ wizard/                        ← NOT TOUCHED (isolated)
  ❌ .vibe/config.toml             ← NOT TOUCHED (we control)
```

### After Merge + Validation

```bash
git merge upstream/main
# Conflict? Only in vibe/* files we don't own

pip install -e .[udos-wizard]
# Re-installs new mistralai, new vibe deps

python -c "... validate tool discovery ..."
# If BaseTool API changed:
#   - Our _base.py might throw TypeError
#   - Easy fix: one-line change in async signature or import
#   - Not our tools themselves, just the wrapper

vibe -p "Check health"
# Either works ✅ or fails with clear error (easy to debug)
```

---

## Summary

| Question | Answer |
|----------|--------|
| Will new vibe slot right in? | **Yes, 95% of the time.** |
| Do we need to prep now? | **No.** Current architecture handles it. |
| What could go wrong? | Very minimal (BaseTool API changes are rare & announced). |
| How do we handle it when it happens? | Follow the merge procedure above (5 min). |
| Should we version-lock vibe? | **Recommended:** Keep `mistralai==1.9.11` pinned, merge major releases manually. |

**You're in great shape.** The addon model really does insulate you from vibe's evolution. When 2.3.0 comes out, you'll merge in an afternoon and everything will just work.

If you want extra confidence, run the optional validation checks above. Otherwise, you're good to go.
