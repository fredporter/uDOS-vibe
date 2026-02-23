# uDOS UI App - Alpine Packaging

The uDOS UI app packaging for Alpine Linux diskless systems.

## Build Environment

### Dependencies

```bash
apk update
apk add cargo rustc nodejs npm python3 python3-dev
apk add gtk+3.0-dev webkit2gtk-dev libxkbcommon-dev
```

### Build Steps

```bash
cd distribution/apkbuild/udos-ui/

# Fetch upstream (uMarkdown-app repo)
abuild fetch

# Verify checksums
abuild checksum

# Build binary
abuild -r

# Install locally
sudo apk add --allow-untrusted ~/packages/$(uname -m)/udos-ui-*.apk
```

## UI Runtime Requirements

### Core Libraries

- **Cage** (Wayland compositor): Single-app mode
- **webkit2gtk** or equivalent browser engine for the UI WebView
- **libxkbcommon** (keyboard handling)
- **mesa** (GPU drivers)
- **libinput** (input device handling)

### Graphics Support

The APKBUILD automatically includes:
- DRI drivers for Intel/AMD GPUs
- Modesetting support (Wayland-native)
- Minimal font set (ttf-dejavu)

### Performance Optimization

For Alpine diskless systems, we keep the UI binary lean:
- No desktop environment dependencies
- Minimal GTK+ (only what the UI needs)
- No redundant libraries from full WebKitGTK stack

## Installation on Physical Hardware

Once built and packaged:

```bash
# Mount persistence
udos-persist mount

# Install UI app
apk add udos-ui

# Enable GUI tier
udos-tier switch gui

# Reboot to activate
reboot
```

## Troubleshooting

### Binary won't start

Check if graphics stack is available:
```bash
udos-gui start
```

This will verify:
- DRI drivers presence
- Wayland libraries
- seatd running
- XDG_RUNTIME_DIR setup

### Build fails

Ensure all dependencies are installed:
```bash
abuild deps
abuild -R
```

### WebView rendering issues

Verify WebKitGTK installation:
```bash
ldconfig -p | grep webkit
apk list --installed | grep webkit
```

For Alpine edge, you may need:
```bash
apk add webkit2gtk-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community
```

## Cross-Compilation

For different architectures:

```bash
# Modify APKBUILD
arch="aarch64 armhf armv7"

# Build for arm64
abuild -r -m aarch64
```

Supported Alpine architectures:
- `x86_64` (Intel/AMD 64-bit)
- `aarch64` (ARM 64-bit, Raspberry Pi 4+)
- `armhf` (ARM 32-bit, older RPi)

## Build Features (Optional)

For lightweight builds on constrained hardware, use a minimal feature set in the UI build configuration.

## Post-Install Verification

```bash
# Check installation
apk list --installed | grep udos-ui

# Test binary
/usr/local/bin/udos-ui --version

# Run via launcher
udos-gui start
```
