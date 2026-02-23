#!/bin/bash
#
# Sonic Stick Download Payloads Script (Ventoy-free)
# Downloads ISO and Raspberry Pi images for Sonic payload assembly.
#
# Usage: bash scripts/download-payloads.sh
#

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISOS_DIR="$BASE_DIR/ISOS"
RASPI_DIR="$BASE_DIR/RaspberryPi"

# Create directories
mkdir -p "$ISOS_DIR/Minimal" "$ISOS_DIR/Rescue" "$ISOS_DIR/Ubuntu" "$RASPI_DIR"

echo "Sonic Stick payload download starting"
echo "Base directory: $BASE_DIR"
echo ""

# Format: "destination|url"
declare -a DOWNLOADS=(
  "$ISOS_DIR/Rescue/CorePure64-15.0.iso|http://tinycorelinux.net/15.x/x86_64/release/CorePure64-15.0.iso"
  "$ISOS_DIR/Minimal/alpine-standard-3.19.1-x86_64.iso|https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-standard-3.19.1-x86_64.iso"
  "$RASPI_DIR/raspios-bookworm-arm64-lite.img.xz|https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz"
  "$RASPI_DIR/ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz|https://cdimage.ubuntu.com/releases/22.04/release/ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz"
  "$RASPI_DIR/DietPi_RPi234-ARMv8-Bookworm.img.xz|https://dietpi.com/downloads/images/DietPi_RPi234-ARMv8-Bookworm.img.xz"
  "$ISOS_DIR/Ubuntu/ubuntu-22.04.5-desktop-amd64.iso|https://releases.ubuntu.com/jammy/ubuntu-22.04.5-desktop-amd64.iso"
)

echo "Planned downloads (${#DOWNLOADS[@]}):"
for i in "${!DOWNLOADS[@]}"; do
  IFS='|' read -r dest url <<< "${DOWNLOADS[$i]}"
  printf "  [%02d] %s\n" $((i+1)) "$dest"
  printf "       %s\n" "$url"
done
echo ""

total=${#DOWNLOADS[@]}
for i in "${!DOWNLOADS[@]}"; do
  IFS='|' read -r dest url <<< "${DOWNLOADS[$i]}"
  current=$((i+1))

  filename=$(basename "$dest")
  echo "[$current/$total] Downloading: $filename"
  echo "    URL: $url"

  if wget -c --show-progress --progress=bar:force "$url" -O "$dest"; then
    echo "    ✓ Complete"
  else
    echo "    ✗ Failed (check network and URL)"
    exit 1
  fi
  echo ""
done

echo "==================================="
echo "All downloads complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  1. Generate manifest: python3 core/sonic_cli.py plan --usb-device /dev/sdX"
echo "  2. Run: sudo bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json"
echo "  3. Use --dry-run first for safety"
echo ""
