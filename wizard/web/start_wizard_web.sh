#!/bin/bash
# Start Wizard Server runtime (no embedded web app)
# Canonical lifecycle now routes through bin/wizardd.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -x "${REPO_ROOT}/bin/wizardd" ]]; then
  echo "wizardd launcher is missing: ${REPO_ROOT}/bin/wizardd" >&2
  exit 1
fi

echo "Starting Wizard Server runtime via wizardd..."
exec "${REPO_ROOT}/bin/wizardd" start
