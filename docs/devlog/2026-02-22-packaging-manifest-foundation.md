# Packaging Manifest Foundation (Shared Adapter Contract)

Date: 2026-02-22

## Summary

Established a shared packaging manifest foundation and wired Sonic build surfaces to use it, reducing drift between script/service defaults and creating a single adapter contract entry point for Linux/Windows/mac tracks.

## Changes

- Added canonical root manifest:
  - `packaging.manifest.json`
  - Includes:
    - `version_source` metadata (`version.json` field priority)
    - `offline_assets` metadata (distribution + memory namespace)
    - per-platform adapters:
      - Linux (`sonic_stick`, `tinycore_installer`)
      - Windows (`entertainment` scripts root)
      - mac (independent companion app note)
- Added shared loader service:
  - `core/services/packaging_manifest_service.py`
  - Returns merged defaults + repo overrides
- Wired manifest into Sonic build service:
  - `wizard/services/sonic_build_service.py`
  - Resolves `default_profile`, `build_script`, and `builds_root` from manifest
- Wired manifest into Sonic build script:
  - `distribution/alpine-core/build-sonic-stick.sh`
  - Uses manifest `linux.sonic_stick.default_profile` when `--profile` is not supplied
- Added tests:
  - `core/tests/packaging_manifest_service_test.py`
  - Extended `wizard/tests/sonic_build_service_artifacts_test.py` with manifest-default profile assertion

## Validation

Executed:

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

- Move `distribution/installer.sh` tier/package mapping to manifest-driven adapter reads.
- Normalize Windows PowerShell packaging scripts against manifest entries to reduce duplicate mode/package definitions.
