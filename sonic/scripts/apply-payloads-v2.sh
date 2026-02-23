#!/bin/bash
# Sonic Screwdriver v2 payload application (Ventoy-free)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MANIFEST=""
DRY_RUN=0
PAYLOADS_DIR=""
NO_VALIDATE=0

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
    --payloads-dir)
      PAYLOADS_DIR="$2"
      shift 2
      ;;
    --no-validate)
      NO_VALIDATE=1
      shift 1
      ;;
    *)
      shift 1
      ;;
  esac
done

source "${SCRIPT_DIR}/lib/logging.sh"
init_logging "apply-payloads-v2"
exec > >(tee -a "$LOG_FILE") 2>&1

OS_NAME="$(sonic_detect_os)"
if [[ "$OS_NAME" != "alpine" && "$OS_NAME" != "ubuntu" ]]; then
  log_error "Unsupported OS: $OS_NAME (requires Alpine/Ubuntu Linux)"
  exit 1
fi

if [[ -z "$MANIFEST" || ! -f "$MANIFEST" ]]; then
  log_error "Manifest not found. Use --manifest <path>."
  exit 1
fi

PAYLOAD_DIR="$(python3 - "$MANIFEST" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r') as f:
    data=json.load(f)
print(data.get('payload_dir',''))
PY
)"

if [[ -n "$PAYLOADS_DIR" ]]; then
  PAYLOAD_DIR="$PAYLOADS_DIR"
fi

if [[ -z "$PAYLOAD_DIR" ]]; then
  log_warn "payload_dir not set in manifest. Using ${BASE_DIR}/payloads"
  PAYLOAD_DIR="${BASE_DIR}/payloads"
fi

if [[ ! -d "$PAYLOAD_DIR" ]]; then
  log_error "payload_dir not found: $PAYLOAD_DIR"
  exit 1
fi

PARTS="$(python3 - "$MANIFEST" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r') as f:
    data=json.load(f)
parts=data.get('partitions') or []
for p in parts:
    print("|".join([
        str(p.get('name','')),
        str(p.get('label','')),
        str(p.get('fs','')),
        str(p.get('role','')),
        str(p.get('format',True)),
        str(p.get('image','') or ""),
        str(p.get('payload_dir','') or ""),
    ]))
PY
)"

if [[ "$DRY_RUN" -eq 1 ]]; then
  log_warn "Dry run enabled. No payloads will be written."
  echo "$PARTS" | nl -w2 -s'. '
  exit 0
fi

log_section "Applying payloads"

mount_root="/mnt/sonic-v2"
mkdir -p "$mount_root"

copy_payload_dir() {
  local src="$1"
  local dest="$2"
  if [[ -d "$src" ]]; then
    log_info "Copying payloads from $src"
    sonic_copy "$src/." "$dest/"
  else
    log_warn "Payload directory missing: $src"
  fi
}

resolve_payload_source() {
  local role="$1"
  local override="$2"
  if [[ -n "$override" ]]; then
    if [[ "$override" == /* ]]; then
      echo "$override"
    else
      echo "$BASE_DIR/$override"
    fi
    return 0
  fi
  case "$role" in
    efi) echo "$PAYLOAD_DIR/efi" ;;
    udos) echo "$PAYLOAD_DIR/udos/rw" ;;
    wizard) echo "$PAYLOAD_DIR/wizard" ;;
    windows) echo "$PAYLOAD_DIR/windows" ;;
    media) echo "$PAYLOAD_DIR/media" ;;
    cache) echo "$PAYLOAD_DIR/cache" ;;
    *) echo "" ;;
  esac
}

validate_payload_sources() {
  local missing=0
  IFS=$'\n'
  for line in $PARTS; do
    IFS='|' read -r name label fs role fmt image payload_override <<< "$line"
    if [[ "$fs" == "swap" ]]; then
      continue
    fi
    if [[ "$fs" == "squashfs" ]]; then
      if [[ -n "$image" && ! -f "$BASE_DIR/$image" ]]; then
        log_warn "Missing squashfs image for $label: $BASE_DIR/$image"
        missing=1
      fi
      continue
    fi
    local src
    src="$(resolve_payload_source "$role" "$payload_override")"
    if [[ -n "$src" && ! -d "$src" ]]; then
      log_warn "Missing payload dir for $label: $src"
      missing=1
    fi
  done
  if [[ $missing -ne 0 ]]; then
    log_error "Payload validation failed. Fix missing payloads or use --skip-payloads."
    exit 1
  fi
}

if [[ "$NO_VALIDATE" -eq 0 ]]; then
  validate_payload_sources
else
  log_warn "Payload validation disabled (--no-validate)."
fi

IFS=$'\n'
for line in $PARTS; do
  IFS='|' read -r name label fs role fmt image payload_override <<< "$line"
  if [[ -z "$label" ]]; then
    continue
  fi
  part="$(detect_partition_by_label "$label" || true)"
  if [[ -z "$part" ]]; then
    log_warn "Partition with label $label not found."
    continue
  fi

  if [[ "$fs" == "swap" ]]; then
    log_info "Skipping payloads for swap partition $label"
    continue
  fi

  if [[ "$fs" == "squashfs" ]]; then
    if [[ -n "$image" && -f "$BASE_DIR/$image" ]]; then
      log_info "Writing squashfs image to $part ($label)"
      dd if="$BASE_DIR/$image" of="$part" bs=4M status=progress conv=fsync
    else
      log_warn "No squashfs image found for $label (expected $BASE_DIR/$image)"
    fi
    continue
  fi

  mnt="$mount_root/$label"
  mkdir -p "$mnt"
  if ! mount "$part" "$mnt"; then
    log_warn "Failed to mount $part at $mnt"
    continue
  fi

  payload_src="$(resolve_payload_source "$role" "$payload_override")"
  if [[ -n "$payload_src" ]]; then
    copy_payload_dir "$payload_src" "$mnt"
  else
    log_info "No payload mapping for role '$role' ($label)"
  fi

  sync
  umount "$mnt" || true
  rmdir "$mnt" 2>/dev/null || true

done

log_ok "Payload application complete."
