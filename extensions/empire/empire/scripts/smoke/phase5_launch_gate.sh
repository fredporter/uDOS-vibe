#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHONPATH_ROOT="${PYTHONPATH_ROOT:-${ROOT_DIR}/..}"
cd "${ROOT_DIR}"

echo "[1/6] API smoke"
scripts/smoke/run_phase2_api_smoke.sh

echo "[2/6] Integration preflight strict"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/smoke/integration_preflight.py --db data/empire.db --strict

echo "[3/6] Integration mocked no-live smoke"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/smoke/integration_no_live_smoke.py

echo "[4/6] DB backup/restore sanity"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/smoke/db_backup_restore_sanity.py --db data/empire.db

echo "[5/6] Web production build"
if [[ ! -d web/node_modules ]]; then
  (cd web && npm install)
fi
(cd web && npm run build)

echo "[6/6] Runtime audit (prod deps)"
(cd web && npm audit --omit=dev)

echo "PASS phase5_launch_gate"
