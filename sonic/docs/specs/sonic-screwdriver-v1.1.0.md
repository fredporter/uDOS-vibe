# uDOS Sonic Screwdriver v1.1.0 (Draft)

## Purpose

Evolve Sonic Screwdriver into a **standalone, decoupleable USB builder** that can be run
as a utility outside uDOS while remaining fully compatible with uDOS + Alpine.

Key goals:
- Replace Ventoy with a **custom, multi-partition layout**.
- Keep uDOS (Alpine TUI) as the smallest self-running control plane.
- Support Windows 10 gaming + media modes (install or boot-from-stick).
- Preserve Ubuntu Wizard support (local orchestration only).
- Expand device database for Windows/media launcher readiness.

---

## Standalone Contract

Sonic Screwdriver should run in isolation from uDOS:
- Own repo + docs + datasets + release artifacts.
- Optional integration hooks for uDOS/Wizard/App.
- No dependency on uDOS internals for basic partition/build operations.

---

## v2 Partition Layout (No Ventoy)

Target: 128 GB USB 3.x (UEFI boot only)

```
[ ESP ]          512 MB   FAT32   (bootloaders + EFI)
[ UDOS_RO ]      8 GB     squashfs (read-only Alpine + uDOS TUI image)
[ UDOS_RW ]      8 GB     ext4     (uDOS persistence)
[ SWAP ]         8 GB     swap     (hibernation + memory pressure)
[ WIZARD ]       20 GB    ext4     (Ubuntu Wizard image or rootfs)
[ WIN10 ]        48 GB    NTFS     (Windows 10 install or WTG)
[ MEDIA ]        28 GB    exFAT    (ROMs, ISOs, media, installers)
[ CACHE ]        ~7.5 GB  ext4     (logs, downloads, temp)
```

### Layout Overrides

Partition sizes and formatting are adjustable via:
- `config/sonic-layout.json` (preferred)
- `--layout-file` and `--format-mode` in `core/sonic_cli.py`
 - `auto_scale` to fit smaller devices by scaling marked partitions

### v2 Partitioning Script

`scripts/partition-layout.sh` consumes the manifest layout and applies GPT partitions,
validating size totals and enforcing a single remainder partition.

### Payload Application

`scripts/apply-payloads-v2.sh` mounts partitions by label and copies payloads from
`payloads/` based on partition role. Squashfs partitions are written directly.

Per-partition overrides can be set with `payload_dir` in `config/sonic-layout.json`.
The v2 launcher supports `--payloads-dir` to override the base payload root.
Use `--no-validate-payloads` as an escape hatch to bypass payload validation.

### Windows 10 Modes
- **install**: store Windows ISO + drivers, installer boots from ESP.
- **wtg**: Windows To Go style NTFS partition for direct boot (hardware dependent).

### Boot Priority
1) uDOS Alpine (default)
2) Windows 10 (gaming / media)
3) Ubuntu Wizard

---

## uDOS TUI (Smallest Self-Running Form)

- Alpine Linux base
- ncurses-first UI
- Single fullscreen process
- Controls partitioning, install, boot routing, device scanning

---

## Windows 10 Gaming + Media Layer

**Gaming:**
- Epic Games Launcher + Fortnite
- GPU drivers + DirectX + VC++ runtimes
- Telemetry reduced, auto-updates disabled (best effort)

**Media:**
- Kodi as 10-foot shell
- WantMyMTV kiosk launcher
- Plex optional
- Remote-first UX

Windows is treated as a sealed console OS with an explicit launcher.

---

## uDOS Windows Launcher (Provisioned)

A uDOS-managed launcher that can:
- Reboot-to-Windows
- Maintain Windows boot profile (gaming vs media)
- Sync launcher metadata to Wizard Server

---

## Sonic Device Database Updates

Add capability flags to improve guidance for Windows/media readiness:
- `windows10_boot`: none / install / wtg / unknown
- `media_mode`: none / htpc / retro / unknown
- `udos_launcher`: none / basic / advanced / unknown

---

## Svelte UI Shell (Dark)

A standalone Sonic UI should be built in **Svelte + Tailwind (dark)** for:
- Boot mode selector (uDOS / Windows / Wizard)
- Build plans + progress
- Device database browser

---

## Non-Goals

- No cloud dependencies in core builder
- No GUI required for build operations
- No Windows changes outside designated partitions

---

## Deliverables

- Custom partitioning scripts (no Ventoy)
- Bootloader config for multi-OS layout
- uDOS TUI minimal image pipeline
- Windows launcher + mode selector
- Updated datasets + schema
- Standalone docs + release packaging
