#!/bin/bash
# Verify Sonic Stick USB layout (Ventoy-free)
# Usage: sudo bash scripts/verify-usb-layout.sh /dev/sdX

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"

USB_DEVICE="${1:-${USB:-/dev/sdb}}"
MNT_DIR="/mnt/sonic-verify"
PASS=1

echo "[Verify] Target USB: ${USB_DEVICE}"
if [[ ! -b "${USB_DEVICE}" ]]; then
  echo "[Error] Device not found: ${USB_DEVICE}" >&2
  exit 1
fi

echo "[Info] Partition table:"
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT "${USB_DEVICE}" | sed '1!s/^/  /'

ESP_PART="$(detect_partition_by_label "ESP" || true)"
UDOS_RW_PART="$(detect_partition_by_label "UDOS_RW" || true)"
WIZARD_PART="$(detect_partition_by_label "WIZARD" || true)"
MEDIA_PART="$(detect_partition_by_label "MEDIA" || true)"

if [[ -z "$ESP_PART" ]]; then
  echo "  ✗ Missing ESP partition label"
  PASS=0
else
  echo "  ✓ ESP partition found: $ESP_PART"
fi

if [[ -z "$UDOS_RW_PART" ]]; then
  echo "  ✗ Missing UDOS_RW partition label"
  PASS=0
else
  echo "  ✓ UDOS_RW partition found: $UDOS_RW_PART"
fi

if [[ -z "$WIZARD_PART" ]]; then
  echo "  ⚠ Missing WIZARD partition label"
else
  echo "  ✓ WIZARD partition found: $WIZARD_PART"
fi

if [[ -z "$MEDIA_PART" ]]; then
  echo "  ⚠ Missing MEDIA partition label"
else
  echo "  ✓ MEDIA partition found: $MEDIA_PART"
fi

if [[ -n "$ESP_PART" ]]; then
  mkdir -p "${MNT_DIR}/esp"
  if mount -o ro "$ESP_PART" "${MNT_DIR}/esp" 2>/dev/null; then
    echo "[Check] ESP boot payload"
    if [[ -f "${MNT_DIR}/esp/EFI/BOOT/BOOTX64.EFI" ]]; then
      echo "  ✓ EFI/BOOT/BOOTX64.EFI present"
    else
      echo "  ⚠ EFI bootloader not found at EFI/BOOT/BOOTX64.EFI"
      PASS=0
    fi
    umount "${MNT_DIR}/esp" || true
  else
    echo "  ✗ Could not mount ESP partition"
    PASS=0
  fi
fi

if [[ -n "$UDOS_RW_PART" ]]; then
  mkdir -p "${MNT_DIR}/udos_rw"
  if mount -o ro "$UDOS_RW_PART" "${MNT_DIR}/udos_rw" 2>/dev/null; then
    echo "[Check] UDOS_RW payload structure"
    # Non-fatal informative checks only.
    for d in memory config logs; do
      if [[ -d "${MNT_DIR}/udos_rw/$d" ]]; then
        echo "  ✓ $d/ present"
      else
        echo "  ⚠ $d/ missing"
      fi
    done
    umount "${MNT_DIR}/udos_rw" || true
  else
    echo "  ✗ Could not mount UDOS_RW partition"
    PASS=0
  fi
fi

rm -rf "$MNT_DIR" 2>/dev/null || true

if [[ "$PASS" -eq 1 ]]; then
  echo "[Result] USB layout looks correct ✅"
  exit 0
fi

echo "[Result] Issues detected with USB layout ⚠"
exit 4
