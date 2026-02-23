#!/usr/bin/env bash
set -euo pipefail

# One-command Phase 2 API smoke run.
# Auto-detects token mode from `EMPIRE_API_TOKEN` or secret store.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8991}"
BASE_URL="http://${API_HOST}:${API_PORT}"
PYTHONPATH_ROOT="${PYTHONPATH_ROOT:-${ROOT_DIR}/..}"
AUTH_TOKEN="${EMPIRE_API_TOKEN:-}"

cd "${ROOT_DIR}"

if [[ -z "${AUTH_TOKEN}" ]]; then
  AUTH_TOKEN="$(PYTHONPATH="${PYTHONPATH_ROOT}" python3 - <<'PY'
from empire.services.secret_store import get_secret
print(get_secret("empire_api_token") or "")
PY
)"
fi

start_api() {
  if [[ -n "${AUTH_TOKEN}" ]]; then
    EMPIRE_API_TOKEN="${AUTH_TOKEN}" \
    PYTHONPATH="${PYTHONPATH_ROOT}" \
    python3 -m uvicorn empire.api.server:app --host "${API_HOST}" --port "${API_PORT}" &
  else
    PYTHONPATH="${PYTHONPATH_ROOT}" \
    python3 -m uvicorn empire.api.server:app --host "${API_HOST}" --port "${API_PORT}" &
  fi
  API_PID=$!
}

wait_api() {
  local attempts=20
  local i
  for ((i=0; i<attempts; i++)); do
    if AUTH_TOKEN="${AUTH_TOKEN}" python3 - <<PY >/dev/null 2>&1
import urllib.request
token = "${AUTH_TOKEN}"
headers = {"Authorization": f"Bearer {token}"} if token else {}
req = urllib.request.Request("${BASE_URL}/health", headers=headers)
urllib.request.urlopen(req)
PY
    then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then
    kill "${API_PID}" >/dev/null 2>&1 || true
    wait "${API_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

start_api

if [[ -n "${AUTH_TOKEN}" ]]; then
  wait_api
  python3 scripts/smoke/api_smoke.py --base-url "${BASE_URL}" --token "${AUTH_TOKEN}" --expect-auth
else
  wait_api
  python3 scripts/smoke/api_smoke.py --base-url "${BASE_URL}"
fi
