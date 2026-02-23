#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

exec uv run python -m core.services.packaging_adapters.cli \
  linux build-sonic-stick \
  --repo-root "${REPO_ROOT}" \
  "$@"

