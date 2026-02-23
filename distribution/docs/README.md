# Distribution Documentation

**TinyCore Linux packaging and distribution system**

## Public Distribution Files

The `/distribution` folder contains public-facing packaging tools:

- **[installer.sh](../installer.sh)** - Main installer script
- **[remaster_iso.sh](../remaster_iso.sh)** - ISO remastering tool
- **[launchers/](../launchers/)** - Platform-specific launch scripts
- **[schemas/](../schemas/)** - Package schemas
- **[templates/](../templates/)** - Package templates
- **[stacks/](../stacks/)** - Installation tier configs

## Documentation

- [README.md](../README.md) - TCZ packaging architecture
- [PACKAGE-TIERS.md](../PACKAGE-TIERS.md) - Installation tiers guide

## Build Artifacts (Wizard-Only)

Build outputs and test packages are in `/wizard/distribution/`:

- **test/** - Test TCZ packages (udos-core.tcz, udos-api.tcz, etc)
- **builds/** - Compiled distribution outputs
- **plugins/** - Dev-only plugins (devstral, cache)

See [/wizard/distribution/](../../wizard/distribution/) for build artifacts.

---

**Last Updated:** 2026-01-15
