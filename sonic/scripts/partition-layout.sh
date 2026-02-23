#!/bin/bash
# Sonic Screwdriver v2 partitioning (Ventoy-free)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MANIFEST=""
DRY_RUN=0

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
    *)
      shift 1
      ;;
  esac
done

source "${SCRIPT_DIR}/lib/logging.sh"
init_logging "partition-layout"
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

USB="$(python3 - "$MANIFEST" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r') as f:
    data=json.load(f)
print(data.get('usb_device',''))
PY
)"

if [[ -z "$USB" || ! -b "$USB" ]]; then
  log_error "USB device '$USB' not found or not a block device."
  exit 1
fi

DEVICE_BYTES="$(lsblk -b -dn -o SIZE "$USB" 2>/dev/null || echo "")"
if [[ -z "$DEVICE_BYTES" ]]; then
  log_error "Unable to read device size for $USB"
  exit 1
fi

PLAN_OUTPUT="$(python3 - "$MANIFEST" "$DEVICE_BYTES" <<'PY'
import json,sys,math
manifest_path=sys.argv[1]
size_bytes=int(sys.argv[2])
size_gib=size_bytes/(1024**3)
with open(manifest_path,'r') as f:
    data=json.load(f)
parts=data.get('partitions') or []
auto_scale=bool(data.get('auto_scale', False))

remainder=[p for p in parts if p.get('remainder')]
if len(remainder) > 1:
    print("STATUS|ERROR|more than one remainder partition defined")
    sys.exit(2)

fixed=[p for p in parts if not p.get('remainder')]
fixed_sum=sum(float(p.get('size_gb',0) or 0) for p in fixed)

scalable=[p for p in fixed if p.get('scalable')]
non_scalable=[p for p in fixed if not p.get('scalable')]

min_total=sum(float(p.get('min_size_gb',0) or 0) for p in scalable)
non_scale_total=sum(float(p.get('size_gb',0) or 0) for p in non_scalable)

message=f"device={size_gib:.2f}GiB fixed={fixed_sum:.2f}GiB"

if fixed_sum > size_gib:
    if not scalable:
        print(f"STATUS|ERROR|fixed sizes exceed device ({message})")
        sys.exit(3)
    if (non_scale_total + min_total) > size_gib:
        print(f"STATUS|ERROR|min sizes exceed device ({message})")
        sys.exit(4)
    available=size_gib - non_scale_total
    scale_base=sum(float(p.get('size_gb',0) or 0) for p in scalable)
    scale_factor=available/scale_base if scale_base else 1.0
    for p in scalable:
        target=float(p.get('size_gb',0) or 0)*scale_factor
        min_sz=float(p.get('min_size_gb',0) or 0)
        max_sz=p.get('max_size_gb')
        if max_sz is not None:
            max_sz=float(max_sz)
            target=min(target, max_sz)
        target=max(target, min_sz)
        p['size_gb']=round(target,2)
    fixed_sum=sum(float(p.get('size_gb',0) or 0) for p in fixed)
    message=f"device={size_gib:.2f}GiB scaled_fixed={fixed_sum:.2f}GiB"
    if not auto_scale:
        print(f"STATUS|SUGGEST|sizes exceed device; enable auto_scale or adjust layout ({message})")
    else:
        print(f"STATUS|OK|auto-scaled to fit ({message})")
elif fixed_sum < size_gib and not remainder:
    if scalable:
        available=size_gib - non_scale_total
        scale_base=sum(float(p.get('size_gb',0) or 0) for p in scalable)
        scale_factor=available/scale_base if scale_base else 1.0
        for p in scalable:
            target=float(p.get('size_gb',0) or 0)*scale_factor
            p['size_gb']=round(target,2)
        fixed_sum=sum(float(p.get('size_gb',0) or 0) for p in fixed)
        if not auto_scale:
            print(f"STATUS|SUGGEST|unused space detected; add remainder or enable auto_scale ({message})")
        else:
            print(f"STATUS|OK|auto-scaled to use device ({message})")
    else:
        print(f"STATUS|SUGGEST|unused space detected; add remainder partition ({message})")
else:
    print(f"STATUS|OK|layout fits ({message})")

for p in parts:
    print("PART|" + "|".join([
        str(p.get('name','')),
        str(p.get('label','')),
        str(p.get('fs','')),
        str(p.get('size_gb','')),
        str(p.get('remainder',False)),
        str(p.get('format',True)),
        ",".join(p.get('flags',[]) or []),
        str(p.get('role','')),
        str(p.get('image','') or ""),
    ]))
PY
)"

status_line="$(echo "$PLAN_OUTPUT" | head -n1)"
status_type="$(echo "$status_line" | cut -d'|' -f2)"
status_msg="$(echo "$status_line" | cut -d'|' -f3-)"

if [[ "$status_type" == "ERROR" ]]; then
  log_error "$status_msg"
  exit 1
fi

if [[ "$status_type" == "SUGGEST" ]]; then
  log_warn "$status_msg"
else
  log_info "$status_msg"
fi

PARTS="$(echo "$PLAN_OUTPUT" | tail -n +2 | sed 's/^PART|//')"

if [[ "$DRY_RUN" -eq 1 ]]; then
  log_warn "Dry run enabled. No partitioning will occur."
  echo "Planned partitions:"
  echo "$PARTS" | nl -w2 -s'. '
  exit 0
fi

if [[ "$status_type" == "SUGGEST" ]]; then
  log_warn "Layout requires adjustment. Edit config/sonic-layout.json or set auto_scale=true."
  exit 1
fi

FORMAT_MODE="$(python3 - "$MANIFEST" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r') as f:
    data=json.load(f)
print(data.get('format_mode','full'))
PY
)"

if [[ "$FORMAT_MODE" == "skip" ]]; then
  log_warn "Format mode is 'skip' - partition table will still be created, formatting skipped."
fi

if ! command -v sgdisk >/dev/null 2>&1; then
  log_error "sgdisk is required for GPT partitioning (install gdisk)."
  exit 1
fi

log_section "Creating GPT layout"
log_warn "This will DESTROY all data on $USB"

sgdisk --zap-all "$USB"
sgdisk -o "$USB"

idx=1
IFS=$'\n'
for line in $PARTS; do
  IFS='|' read -r name label fs size_gb remainder fmt flags role image <<< "$line"
  if [[ "$remainder" == "True" || "$remainder" == "true" ]]; then
    sgdisk --new=${idx}:0:0 "$USB"
  else
    sgdisk --new=${idx}:0:+${size_gb}G "$USB"
  fi

  case "$fs" in
    fat32) sgdisk --typecode=${idx}:ef00 "$USB" ;;
    swap) sgdisk --typecode=${idx}:8200 "$USB" ;;
    ntfs) sgdisk --typecode=${idx}:0700 "$USB" ;;
    *) sgdisk --typecode=${idx}:8300 "$USB" ;;
  esac

  if [[ -n "$label" ]]; then
    sgdisk --change-name=${idx}:"${label}" "$USB"
  fi
  idx=$((idx+1))
done

partprobe "$USB" || true
sleep 2

log_section "Formatting partitions"
idx=1
for line in $PARTS; do
  IFS='|' read -r name label fs size_gb remainder fmt flags role image <<< "$line"
  part="$USB$idx"
  if [[ "$USB" == *"nvme"* ]]; then
    part="${USB}p${idx}"
  fi
  if [[ "$fmt" == "False" || "$fmt" == "false" || "$FORMAT_MODE" == "skip" ]]; then
    log_warn "Skipping format for $part ($label)"
    idx=$((idx+1))
    continue
  fi

  case "$fs" in
    fat32)
      mkfs.fat -F32 -n "$label" "$part"
      ;;
    ext4)
      mkfs.ext4 -F -L "$label" "$part"
      ;;
    exfat)
      if command -v mkfs.exfat >/dev/null 2>&1; then
        mkfs.exfat -n "$label" "$part"
      else
        mkexfatfs -n "$label" "$part"
      fi
      ;;
    ntfs)
      mkfs.ntfs -F -L "$label" "$part"
      ;;
    swap)
      mkswap -L "$label" "$part"
      ;;
    squashfs)
      log_warn "Skipping squashfs formatting for $part ($label); expected image write."
      ;;
    *)
      log_warn "Unknown fs '$fs' for $part; skipping format."
      ;;
  esac

  idx=$((idx+1))
done

log_ok "Partition layout applied successfully."
