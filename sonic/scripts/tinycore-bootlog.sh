#!/bin/bash
#
# TinyCore Boot Logging Hook
# Logs boot info (dmesg, lsblk, hardware details) to exFAT partition
#
# Usage: Place in TinyCore /opt/bootlocal.sh or call manually
# Logs to: /mnt/sdX2/LOGS/boot.log
#

MOUNTPOINT="/media/SONIC"

# Prefer FLASH if mounted (ext4 is safer for logs)
if [[ -d "/media/FLASH" ]]; then
  MOUNTPOINT="/media/FLASH"
fi

LOGFILE="$MOUNTPOINT/LOGS/boot.log"

# Try to find exFAT mount
if [[ ! -d "$MOUNTPOINT" ]]; then
  # Fallback: search for SONIC label
  MOUNTPOINT=$(mount | grep -i sonic | awk '{print $3}' | head -1)
fi

if [[ -z "$MOUNTPOINT" ]] || [[ ! -d "$MOUNTPOINT" ]]; then
  echo "ERROR: Could not find SONIC exFAT partition"
  exit 1
fi

# Create LOGS directory
mkdir -p "$MOUNTPOINT/LOGS"

# Append boot log
{
  echo ""
  echo "==============================================="
  date
  echo "==============================================="
  echo ""
  echo "=== Hardware Info ==="
  lsblk
  echo ""
  echo "=== Kernel Messages ==="
  dmesg | tail -50
  echo ""
  echo "=== Network ==="
  ip a 2>/dev/null || ifconfig
  echo ""
} >> "$LOGFILE"

echo "Boot log saved to: $LOGFILE"
echo "Entries: $(wc -l < "$LOGFILE")"
