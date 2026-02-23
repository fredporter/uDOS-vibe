# Recovery & Diagnostics (Windows 10 Entertainment Stack)

This folder defines recovery hooks for restoring Media/Game mode images and gathering diagnostics.

## Goals
- Restore Media/Game partitions from known-good images.
- Provide quick health checks for drivers, controller, and boot configuration.
- Avoid destructive actions unless explicitly executed.

## Scripts
- `restore-media-image.ps1` — applies the Media Mode image to the WINDOWS_MEDIA partition.
- `restore-game-image.ps1` — applies the Game Mode image to the WINDOWS_GAMES partition.
- `diagnostics.ps1` — gathers boot config and controller diagnostics.

All scripts are non-destructive unless `-Execute` is passed.
