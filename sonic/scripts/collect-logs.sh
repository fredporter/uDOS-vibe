#!/bin/bash
# Sonic Stick - Support log collector
# Gathers host info plus Sonic Stick metadata into LOGS/collect-<timestamp>
# Usage: sudo bash scripts/collect-logs.sh [device]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${SCRIPT_DIR}/lib/logging.sh"
init_logging "collect-logs"
exec > >(tee -a "$LOG_FILE") 2>&1

if [[ $EUID -ne 0 ]]; then
  log_error "Run as root (sudo) so we can mount the stick"
  exit 1
fi

# Detect device if not supplied
DEVICE="${1:-}"
if [[ -z "$DEVICE" ]]; then
  DEVICE=$(lsblk -rpo NAME,LABEL | awk '$2=="SONIC" {print $1; exit}')
fi

if [[ -z "$DEVICE" ]]; then
  log_error "Could not auto-detect device. Pass /dev/sdX (e.g., /dev/sdb)."
  exit 1
fi

part_path() {
  local base="$1" num="$2"
  if [[ "$base" =~ (nvme|mmcblk) ]]; then
    echo "${base}p${num}"
  else
    echo "${base}${num}"
  fi
}

WORKDIR=$(mktemp -d /tmp/sonic-collect-XXXX)
COLLECT_DIR="${LOG_ROOT}/collect-$(date -Iseconds)"
mkdir -p "$COLLECT_DIR"
log_section "Collecting logs to $COLLECT_DIR"

cleanup() {
  set +e
  umount "$WORKDIR/media" 2>/dev/null || true
  umount "$WORKDIR/data" 2>/dev/null || true
  umount "$WORKDIR/efi" 2>/dev/null || true
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

mkdir -p "$WORKDIR"/{media,data,efi}

log_env_snapshot

lsblk -f > "$COLLECT_DIR/lsblk.txt"
blkid > "$COLLECT_DIR/blkid.txt" 2>/dev/null || true
dmesg | tail -200 > "$COLLECT_DIR/dmesg-tail.txt" 2>/dev/null || true

ESP_PART=$(detect_partition_by_label "ESP" || true)
MEDIA_PART=$(detect_partition_by_label "MEDIA" || true)
DATA_PART=$(detect_partition_by_label "UDOS_RW" || true)

if [[ -z "$ESP_PART" ]]; then
  ESP_PART=$(part_path "$DEVICE" 1)
fi
if [[ -z "$MEDIA_PART" ]]; then
  MEDIA_PART=$(part_path "$DEVICE" 7)
fi
if [[ -z "$DATA_PART" ]]; then
  DATA_PART=$(part_path "$DEVICE" 3)
fi

if [ -b "$MEDIA_PART" ]; then
  log_info "Mounting MEDIA partition $MEDIA_PART"
  mount -o ro "$MEDIA_PART" "$WORKDIR/media" || log_warn "Could not mount $MEDIA_PART"
  find "$WORKDIR/media" -maxdepth 3 -type f -name "*.iso" -printf '%P\n' | sort > "$COLLECT_DIR/iso-list.txt" || true
fi

if [ -b "$ESP_PART" ]; then
  log_info "Mounting ESP partition $ESP_PART"
  mount -o ro "$ESP_PART" "$WORKDIR/efi" || true
  [ -f "$WORKDIR/efi/EFI/BOOT/BOOTX64.EFI" ] && cp "$WORKDIR/efi/EFI/BOOT/BOOTX64.EFI" "$COLLECT_DIR/BOOTX64.EFI" || true
fi

if [ -b "$DATA_PART" ]; then
  log_info "Mounting data partition $DATA_PART"
  mount -o ro "$DATA_PART" "$WORKDIR/data" || true
  if [ -d "$WORKDIR/data/logs" ]; then
    mkdir -p "$COLLECT_DIR/data-logs"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --exclude '*.iso' "$WORKDIR/data/logs/" "$COLLECT_DIR/data-logs/" || true
    else
      log_warn "rsync not found; using cp for data logs"
      cp -a "$WORKDIR/data/logs/." "$COLLECT_DIR/data-logs/" || true
    fi
  fi
  for f in config/sonic-stick.conf library/iso-catalog.json README.txt; do
    [ -f "$WORKDIR/data/$f" ] && mkdir -p "$COLLECT_DIR/$(dirname "$f")" && cp "$WORKDIR/data/$f" "$COLLECT_DIR/$f"
  done
fi

log_ok "Support bundle available at $COLLECT_DIR"
log_info "Include $COLLECT_DIR when reporting boot issues."
