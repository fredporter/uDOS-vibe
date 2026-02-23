#!/bin/bash
#
# Sonic Stick - Create Data Partition
# Creates a 3rd partition on the USB stick for logs, sessions, and library tracking
#
# Usage: sudo bash scripts/create-data-partition.sh [device]
# Example: sudo bash scripts/create-data-partition.sh /dev/sdb
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${SCRIPT_DIR}/lib/logging.sh"
init_logging "create-data-partition"
exec > >(tee -a "$LOG_FILE") 2>&1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info "Starting data partition creation"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

DEVICE=$1

if [ -z "$DEVICE" ]; then
    echo -e "${YELLOW}Available USB devices:${NC}"
    lsblk -d -o NAME,SIZE,TYPE,VENDOR,MODEL | grep -E "sd|nvme"
    echo ""
    echo -e "${BLUE}Usage: sudo bash $0 /dev/sdX${NC}"
    echo -e "${YELLOW}Example: sudo bash $0 /dev/sdb${NC}"
    exit 1
fi

if [ ! -b "$DEVICE" ]; then
    echo -e "${RED}Error: $DEVICE is not a block device${NC}"
    exit 1
fi

# Confirm device
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}Current partitions on $DEVICE:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
lsblk "$DEVICE" -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
echo ""
echo -e "${RED}WARNING: This will create a new partition on $DEVICE${NC}"
echo -e "${YELLOW}Existing data partitions will NOT be affected${NC}"
echo ""
read -p "Continue? (type 'YES' in capitals): " confirm

if [ "$confirm" != "YES" ]; then
    echo -e "${BLUE}Aborted.${NC}"
    exit 0
fi

# Unmount any mounted partitions
echo -e "${BLUE}Unmounting partitions...${NC}"
for part in ${DEVICE}*[0-9]; do
    if mountpoint -q "$part" 2>/dev/null || mount | grep -q "$part"; then
        echo "  Unmounting $part"
        umount "$part" 2>/dev/null || true
    fi
done

# Get the last partition number
LAST_PART=$(parted -s "$DEVICE" print | grep -E '^ [0-9]' | tail -1 | awk '{print $1}')
echo -e "${BLUE}Last partition: $LAST_PART${NC}"

# Calculate new partition number
NEW_PART=$((LAST_PART + 1))
DEVICE_NAME=$(basename "$DEVICE")

# Determine partition naming (sdb vs nvme)
if [[ "$DEVICE" =~ nvme ]]; then
    NEW_PART_PATH="${DEVICE}p${NEW_PART}"
else
    NEW_PART_PATH="${DEVICE}${NEW_PART}"
fi

echo -e "${BLUE}Creating partition ${NEW_PART} at ${NEW_PART_PATH}...${NC}"

# Get the end of the last partition
END_OF_LAST=$(parted -s "$DEVICE" unit MB print free | grep -E "^ ${LAST_PART}" | awk '{print $3}' | sed 's/MB//')
echo "  Last partition ends at: ${END_OF_LAST}MB"

# Create new partition (2GB = 2048MB)
# Using the remaining free space after last partition
START_NEW=$((END_OF_LAST))
SIZE_MB=2048
END_NEW=$((START_NEW + SIZE_MB))

echo -e "${BLUE}Creating ${SIZE_MB}MB ext4 partition...${NC}"
parted -s "$DEVICE" mkpart primary ext4 ${START_NEW}MB ${END_NEW}MB || {
    echo -e "${YELLOW}Trying with remaining space...${NC}"
    parted -s "$DEVICE" mkpart primary ext4 ${START_NEW}MB 100%
}

# Wait for partition to appear
sleep 2
partprobe "$DEVICE" 2>/dev/null || true
sleep 2

# Format partition
echo -e "${BLUE}Formatting ${NEW_PART_PATH} as ext4...${NC}"
mkfs.ext4 -L "FLASH" "$NEW_PART_PATH"

# Create mount point and mount
MOUNT_POINT="/mnt/sonic-data"
mkdir -p "$MOUNT_POINT"
mount "$NEW_PART_PATH" "$MOUNT_POINT"

# Create directory structure
echo -e "${BLUE}Creating directory structure...${NC}"
mkdir -p "$MOUNT_POINT"/{logs,sessions,library,devices,config}

# Create initial tracking files
cat > "$MOUNT_POINT/library/iso-catalog.json" << 'EOF'
{
  "last_updated": "$(date -Iseconds)",
  "available_isos": [],
  "installed_oses": [],
  "boot_history": []
}
EOF

cat > "$MOUNT_POINT/devices/hardware-log.json" << 'EOF'
{
  "devices_booted": [],
  "last_scan": "$(date -Iseconds)"
}
EOF

cat > "$MOUNT_POINT/config/sonic-stick.conf" << 'EOF'
# Sonic Stick Configuration
STICK_NAME="SONIC"
DATA_VERSION="1.0"
CREATED="$(date -Iseconds)"
EOF

# Set permissions
chmod -R 755 "$MOUNT_POINT"

# Create README
cat > "$MOUNT_POINT/README.txt" << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║              SONIC STICK - DATA PARTITION                    ║
╚══════════════════════════════════════════════════════════════╝

This partition stores:
  • logs/       - Boot logs and system messages
  • sessions/   - Session data from live boots
  • library/    - ISO catalog and installation tracking
  • devices/    - Hardware detection logs
  • config/     - Sonic Stick configuration

This partition is automatically mounted when you boot any ISO
from the Sonic Stick and can be used to persist data across
live sessions.

Label: FLASH
Filesystem: ext4
Created: $(date)
EOF

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Data partition created successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "Partition: $NEW_PART_PATH"
echo "Label: FLASH"
echo "Mounted at: $MOUNT_POINT"
echo ""
echo "Directory structure:"
tree -L 2 "$MOUNT_POINT" 2>/dev/null || ls -la "$MOUNT_POINT"
echo ""

# Unmount
umount "$MOUNT_POINT"
echo -e "${BLUE}Unmounted. Data partition ready for use.${NC}"
echo ""
echo -e "${YELLOW}Partition layout:${NC}"
lsblk "$DEVICE" -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
