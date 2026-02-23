# Packaging Manifest Windows Wiring (Entertainment Scripts)

Date: 2026-02-22

## Summary

Completed manifest adapter wiring for Windows entertainment scripts by introducing shared manifest readers in `common.ps1` and replacing hardcoded script defaults with manifest-driven values.

## Changes

- Expanded manifest contract:
  - `packaging.manifest.json`
  - Added Windows entertainment adapter fields:
    - `offline_root`
    - `mode_switch` defaults (`media/game identifiers`, partitions, timeout)
    - `shell_paths`
    - `default_game_launcher_path`
- Expanded default manifest loader:
  - `core/services/packaging_manifest_service.py`
  - Added matching fallback defaults for new Windows adapter fields.
- Added shared PowerShell manifest helpers:
  - `distribution/windows10-entertainment/scripts/common.ps1`
  - New helpers:
    - `Get-UdosRepoRoot`
    - `Get-UdosPackagingManifest`
    - `Get-UdosWindowsEntertainmentConfig`
    - `Get-UdosShellPath`
- Wired manifest values into scripts:
  - `distribution/windows10-entertainment/scripts/mode-switch.ps1`
  - `distribution/windows10-entertainment/scripts/install-media-shell.ps1`
  - `distribution/windows10-entertainment/scripts/install-game-launcher.ps1`
  - `distribution/windows10-entertainment/scripts/media-policies.ps1`

## Validation

- Python/regression suite:

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

- Shell syntax checks:

```bash
sh -n distribution/installer.sh
sh -n distribution/alpine-core/build-sonic-stick.sh
```

- Note: local environment does not provide `pwsh`, so PowerShell parser validation was not runnable in this session.
