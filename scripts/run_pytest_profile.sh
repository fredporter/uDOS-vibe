#!/usr/bin/env bash
set -euo pipefail

profile="${1:-full}"
shift || true

case "${profile}" in
  core)
    targets=(core/tests tests)
    ;;
  wizard|full|roadmap)
    targets=(wizard/tests core/tests tests)
    ;;
  *)
    echo "Unknown profile: ${profile}" >&2
    echo "Usage: scripts/run_pytest_profile.sh [core|wizard|full|roadmap] [extra pytest args...]" >&2
    exit 2
    ;;
esac

# Keep test runs deterministic by removing workstation-specific env bleed.
unset UDOS_ROOT
unset USER_NAME
unset USER_ROLE
unset MISTRAL_API_KEY
unset UDOS_LOG_RING

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  "${targets[@]}" "$@"
