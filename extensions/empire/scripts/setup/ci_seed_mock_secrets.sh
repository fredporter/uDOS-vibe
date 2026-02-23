#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHONPATH_ROOT="${PYTHONPATH_ROOT:-${ROOT_DIR}/..}"

mkdir -p "${ROOT_DIR}/config/gmail"
cat > "${ROOT_DIR}/config/gmail/credentials.mock.json" <<'JSON'
{
  "installed": {
    "client_id": "ci-mock-client",
    "project_id": "ci-mock",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "ci-mock-secret",
    "redirect_uris": ["http://localhost"]
  }
}
JSON

cat > "${ROOT_DIR}/config/gmail/token.mock.json" <<'JSON'
{
  "token": "ci-mock-token",
  "refresh_token": "ci-mock-refresh",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "ci-mock-client",
  "client_secret": "ci-mock-secret",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
}
JSON

cd "${ROOT_DIR}"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/setup/set_api_token.py --token 'ci-empire-api-token'
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/setup/set_hubspot_token.py --token 'ci-hubspot-token'
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/setup/set_google_gmail_credentials_path.py --path "${ROOT_DIR}/config/gmail/credentials.mock.json"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/setup/set_google_gmail_token_path.py --path "${ROOT_DIR}/config/gmail/token.mock.json"
PYTHONPATH="${PYTHONPATH_ROOT}" python3 scripts/setup/set_google_places_api_key.py --api-key 'ci-places-key'

echo "PASS ci_seed_mock_secrets"
