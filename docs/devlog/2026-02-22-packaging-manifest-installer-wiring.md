# Packaging Manifest Installer Wiring (TinyCore)

Date: 2026-02-22

## Summary

Wired TinyCore installer tier defaults/package mappings to `packaging.manifest.json`, replacing hardcoded-only tier behavior with manifest-driven resolution while preserving fallback behavior.

## Changes

- Updated manifest contract:
  - `packaging.manifest.json`
  - Added `adapters.linux.tinycore_installer.tiers` mapping for `ultra|micro|mini|core|standard|wizard`.
- Updated shared defaults:
  - `core/services/packaging_manifest_service.py`
  - Added default TinyCore tier package matrix in canonical fallback manifest.
- Updated TinyCore installer:
  - `distribution/installer.sh`
  - Added manifest integration points:
    - `manifest_default_tier()` resolves `default_tier`
    - `tier_packages_from_manifest()` resolves package list per tier
    - `load_manifest_defaults()` applies manifest default before arg parsing
  - Retains existing hardcoded tier/package fallback if manifest missing or `uv` unavailable.

## Validation

- Shell syntax checks:

```bash
sh -n distribution/installer.sh
sh -n distribution/alpine-core/build-sonic-stick.sh
```

- Regression test sweep:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  core/tests/packaging_manifest_service_test.py \
  wizard/tests/sonic_build_service_artifacts_test.py \
  wizard/tests/sonic_linux_launcher_service_test.py \
  wizard/tests/sonic_platform_linux_launcher_test.py -q
```

Result: `13 passed`.

## Remaining Work

- Move Windows packaging PowerShell scripts to consume `packaging.manifest.json` adapter paths/settings.
