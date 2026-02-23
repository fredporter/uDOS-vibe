# uDOS Sonic Screwdriver v1.0.1

## Purpose

Refactor the legacy Sonic Stick Pack into a safer, OS-aware USB builder with clear separation
between planning (core) and execution (bash).

## Architecture

- Core (Python):
  - Validates OS and prerequisites.
  - Writes a manifest that describes target USB and operations.
  - Produces dry-run plans.

- Bash (Linux-only):
  - Performs disk operations (native UEFI partitioning, payload copy).
  - Consumes manifest inputs.

## Manifest

Default location: `config/sonic-manifest.json`

Fields:
- usb_device: target device (e.g., /dev/sdb)
- boot_mode: uefi-native
- labels: SONIC, ESP, FLASH
- dry_run: boolean

## OS Limitations

- Build operations only on Linux (Ubuntu/Debian/Alpine).
- macOS/Windows are unsupported for disk operations.

## v1.0.1 Deliverables

- Core planning tools (manifest + OS checks)
- Bash script supports manifest + dry-run
- Docs reorganized (specs/howto/devlog)
