#!/usr/bin/env bash
# patch-vibe-app.sh — Symlink the global vibe app.py to this repo's version.
#
# WHY THIS EXISTS
# ---------------
# Our dispatch chain extensions (_handle_ucode_command, : and / prefix
# routing) live in vibe/cli/textual_ui/app.py inside this repo.
# The globally-installed `vibe` binary uses its own copy of app.py in the
# uv tool environment. This script replaces that copy with a symlink so the
# global vibe always runs our version.
#
# RE-RUN AFTER: `curl -fsSL https://vibe.mistral.ai/install.sh | sh`
# (a vibe update reinstalls app.py, breaking the symlink)
#
# USAGE
# -----
#   ./bin/patch-vibe-app.sh            # auto-detect vibe install
#   ./bin/patch-vibe-app.sh /path/to/app.py   # explicit target path
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_APP="$REPO_ROOT/vibe/cli/textual_ui/app.py"

# ── Locate global vibe app.py ─────────────────────────────────────────────────
if [[ -n "${1:-}" ]]; then
    GLOBAL_APP="$1"
else
    VIBE_BIN="$(command -v vibe 2>/dev/null || true)"
    if [[ -z "$VIBE_BIN" ]]; then
        echo "ERROR: 'vibe' not found on PATH. Install it first:" >&2
        echo "  curl -fsSL https://vibe.mistral.ai/install.sh | sh" >&2
        exit 1
    fi

    # Follow symlinks to the real binary
    VIBE_REAL="$(python3 -c "import os,sys; print(os.path.realpath('$VIBE_BIN'))")"
    # site-packages is 3 levels up from bin/vibe -> lib/pythonX.Y/site-packages
    SITE_PKG="$(python3 -c "
import pathlib, subprocess, sys
real = pathlib.Path('$VIBE_REAL').resolve()
# walk up until we find site-packages
for p in real.parents:
    if p.name == 'site-packages':
        print(p); sys.exit(0)
# fallback: ask the vibe Python
result = subprocess.run(
    [str(real.parent / 'python'), '-c',
     'import site; print(site.getsitepackages()[0])'],
    capture_output=True, text=True)
print(result.stdout.strip())
")"
    GLOBAL_APP="$SITE_PKG/vibe/cli/textual_ui/app.py"
fi

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [[ ! -f "$REPO_APP" ]]; then
    echo "ERROR: Repo app.py not found: $REPO_APP" >&2
    exit 1
fi

if [[ ! -e "$GLOBAL_APP" && ! -L "$GLOBAL_APP" ]]; then
    echo "ERROR: Global vibe app.py not found: $GLOBAL_APP" >&2
    echo "  Pass the correct path as an argument: $0 /path/to/app.py" >&2
    exit 1
fi

# ── Apply symlink ─────────────────────────────────────────────────────────────
# Backup original only if it's a real file (not already our symlink)
if [[ -f "$GLOBAL_APP" && ! -L "$GLOBAL_APP" ]]; then
    BAK="${GLOBAL_APP}.bak"
    cp "$GLOBAL_APP" "$BAK"
    echo "  Backed up original → $BAK"
fi

ln -sf "$REPO_APP" "$GLOBAL_APP"
echo "  Symlinked: $GLOBAL_APP"
echo "          → $REPO_APP"
echo ""
echo "✓ Done. Global vibe now uses repo app.py."
echo "  Re-run this script after: curl -fsSL https://vibe.mistral.ai/install.sh | sh"
