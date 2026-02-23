#!/bin/bash
# Sonic Stick launcher (Ventoy-free)
# Executes v2 partition layout + payload pipeline only.

set -euo pipefail

VERSION="1.3.17"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MANIFEST=""
DRY_RUN=0
SKIP_PAYLOADS=0
PAYLOADS_ONLY=0
PAYLOADS_DIR=""
NO_VALIDATE_PAYLOADS=0
ORIG_ARGS=("$@")

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      MANIFEST="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift 1
      ;;
    --v2)
      # Backward-compatible no-op: v2 is now always on.
      shift 1
      ;;
    --skip-payloads)
      SKIP_PAYLOADS=1
      shift 1
      ;;
    --payloads-only)
      PAYLOADS_ONLY=1
      shift 1
      ;;
    --payloads-dir)
      PAYLOADS_DIR="$2"
      shift 2
      ;;
    --no-validate-payloads)
      NO_VALIDATE_PAYLOADS=1
      shift 1
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

source "${SCRIPT_DIR}/lib/logging.sh"
OS_NAME="$(sonic_detect_os)"
if [[ "$OS_NAME" != "alpine" && "$OS_NAME" != "ubuntu" ]]; then
  echo "ERROR Sonic Screwdriver requires Linux (Ubuntu/Alpine) for build operations."
  exit 1
fi

if [[ -z "$MANIFEST" ]]; then
  MANIFEST="${BASE_DIR}/config/sonic-manifest.json"
fi

if [[ ! -f "$MANIFEST" ]]; then
  echo "ERROR Manifest not found: $MANIFEST"
  echo "Run: python3 core/sonic_cli.py plan --out config/sonic-manifest.json"
  exit 1
fi

USB="$(python3 - "$MANIFEST" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r') as f:
    data=json.load(f)
print(data.get('usb_device','/dev/sdb'))
PY
)"

# Re-exec with sudo for device access
if [[ $EUID -ne 0 && -z "${SONIC_SUDO_REEXEC:-}" ]]; then
  exec sudo -E SONIC_SUDO_REEXEC=1 USB="$USB" bash "$0" "${ORIG_ARGS[@]}"
fi

init_logging "sonic-stick"
exec > >(tee -a "$LOG_FILE") 2>&1

log_section "Sonic Stick Launcher v${VERSION} (Ventoy-free)"
log_info "Target USB device: $USB"
log_info "Manifest: $MANIFEST"
log_info "Repo: $BASE_DIR"
log_info "Detected OS: $OS_NAME"

if [[ "$PAYLOADS_ONLY" -eq 1 ]]; then
  log_section "Apply payloads only"
  payload_args=(--manifest "$MANIFEST")
  if [[ -n "$PAYLOADS_DIR" ]]; then
    payload_args+=(--payloads-dir "$PAYLOADS_DIR")
  fi
  if [[ "$NO_VALIDATE_PAYLOADS" -eq 1 ]]; then
    payload_args+=(--no-validate)
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    payload_args+=(--dry-run)
  fi
  bash "${SCRIPT_DIR}/apply-payloads-v2.sh" "${payload_args[@]}"
  exit $?
fi

log_section "Apply partition layout"
layout_args=(--manifest "$MANIFEST")
if [[ "$DRY_RUN" -eq 1 ]]; then
  layout_args+=(--dry-run)
fi
bash "${SCRIPT_DIR}/partition-layout.sh" "${layout_args[@]}"

if [[ "$SKIP_PAYLOADS" -eq 1 ]]; then
  log_warn "Skipping payload application (--skip-payloads)"
  exit 0
fi

log_section "Apply payloads"
payload_args=(--manifest "$MANIFEST")
if [[ -n "$PAYLOADS_DIR" ]]; then
  payload_args+=(--payloads-dir "$PAYLOADS_DIR")
fi
if [[ "$NO_VALIDATE_PAYLOADS" -eq 1 ]]; then
  payload_args+=(--no-validate)
fi
if [[ "$DRY_RUN" -eq 1 ]]; then
  payload_args+=(--dry-run)
fi
bash "${SCRIPT_DIR}/apply-payloads-v2.sh" "${payload_args[@]}"

if [[ "$DRY_RUN" -eq 0 ]]; then
  log_section "Verify USB layout"
  bash "${SCRIPT_DIR}/verify-usb-layout.sh" "$USB" || true
fi

log_ok "Sonic Stick workflow complete (Ventoy-free)."
