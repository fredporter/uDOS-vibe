#!/bin/sh
# uDOS TinyCore ISO Remaster
# Creates a bootable ISO with uDOS TCZ packages preloaded.

set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
WORK_DIR="${TMPDIR:-/tmp}/udos-iso"
ISO_INPUT="CorePlus-15.0.iso"
ISO_OUTPUT="uDOS-TinyCore-15.0.iso"
PKG_DIR="${SCRIPT_DIR}/tcz"
ONBOOT_LIST="udos-core.tcz"

usage() {
  cat <<'EOF'
uDOS ISO Remaster

Usage: remaster_iso.sh [--input=CorePlus-15.0.iso] [--output=uDOS-TinyCore.iso] [--packages="p1,p2"] [--from=/path/to/tcz]

Options:
  --input     Path to base TinyCore ISO (default: CorePlus-15.0.iso)
  --output    Output ISO filename (default: uDOS-TinyCore-15.0.iso)
  --packages  Comma-separated package list for onboot (default: udos-core.tcz)
  --from      Directory containing .tcz packages (default: distribution/tcz)
  --help      Show this help
EOF
}

err() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
log() { printf '%s\n' "$*"; }

require_tools() {
  for tool in mkisofs xorriso; do
    if command -v "$tool" >/dev/null 2>&1; then
      MKISOFS="$tool"
      return
    fi
  done
  err "Missing mkisofs/xorriso. Install cdrtools or xorriso."
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --input=*) ISO_INPUT=${1#*=} ;;
      --input) ISO_INPUT=$2; shift ;;
      --output=*) ISO_OUTPUT=${1#*=} ;;
      --output) ISO_OUTPUT=$2; shift ;;
      --packages=*) ONBOOT_LIST=${1#*=} ;;
      --packages) ONBOOT_LIST=$2; shift ;;
      --from=*) PKG_DIR=${1#*=} ;;
      --from) PKG_DIR=$2; shift ;;
      --help|-h) usage; exit 0 ;;
      *) usage; err "Unknown option: $1" ;;
    esac
    shift
  done
}

prepare_dirs() {
  EXTRACT_DIR="$WORK_DIR/extract"
  MOUNT_DIR="$WORK_DIR/mount"
  mkdir -p "$EXTRACT_DIR" "$MOUNT_DIR"
}

mount_and_copy() {
  [ -f "$ISO_INPUT" ] || err "Base ISO not found: $ISO_INPUT"
  sudo mount -o loop "$ISO_INPUT" "$MOUNT_DIR"
  cp -a "$MOUNT_DIR"/* "$EXTRACT_DIR"/
  sudo umount "$MOUNT_DIR"
}

add_packages() {
  [ -d "$PKG_DIR" ] || err "Package directory not found: $PKG_DIR"
  mkdir -p "$EXTRACT_DIR/cde/optional"
  for pkg in $(printf "%s" "$ONBOOT_LIST" | tr ',' ' '); do
    [ -f "$PKG_DIR/$pkg" ] || err "Missing package: $PKG_DIR/$pkg"
    cp "$PKG_DIR/$pkg" "$EXTRACT_DIR/cde/optional/"
    for ext in dep md5.txt info list; do
      f="$PKG_DIR/${pkg%.tcz}.tcz.${ext}"
      [ -f "$f" ] && cp "$f" "$EXTRACT_DIR/cde/optional/"
    done
  done
  # Append onboot list
  mkdir -p "$EXTRACT_DIR/cde"
  for pkg in $(printf "%s" "$ONBOOT_LIST" | tr ',' ' '); do
    echo "$pkg" >> "$EXTRACT_DIR/cde/onboot.lst"
  done
}

build_iso() {
  BOOT_CAT="boot/isolinux/boot.cat"
  BOOT_BIN="boot/isolinux/isolinux.bin"

  (cd "$EXTRACT_DIR" && \
    $MKISOFS \
      -l -J -R -V "uDOS-TinyCore" \
      -no-emul-boot -boot-load-size 4 -boot-info-table \
      -b "$BOOT_BIN" -c "$BOOT_CAT" \
      -o "$SCRIPT_DIR/$ISO_OUTPUT" .)
}

main() {
  parse_args "$@"
  require_tools
  prepare_dirs
  mount_and_copy
  add_packages
  build_iso
  log "✅ ISO created: $SCRIPT_DIR/$ISO_OUTPUT"
  log "Packages on boot: $ONBOOT_LIST"
}

main "$@"
