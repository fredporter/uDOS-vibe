# 2026-02-23 I2: Installer Capability Probes + Hardline Gates

## Scope

Complete I2 from `docs/roadmap.md`: enforce installer capability probes and hardline gating for local-model tiers.

## Changes

- Enhanced host installer preflight in `bin/install-udos-vibe.sh`:
  - Added `--preflight-json` mode (capability/tier decision output without installation).
  - Added explicit probe override env vars for deterministic validation in tests:
    - `UDOS_INSTALLER_PROBE_OS_TYPE`
    - `UDOS_INSTALLER_PROBE_OS_VERSION`
    - `UDOS_INSTALLER_PROBE_KERNEL_VERSION`
    - `UDOS_INSTALLER_PROBE_CPU_ARCH`
    - `UDOS_INSTALLER_PROBE_CPU_CORES`
    - `UDOS_INSTALLER_PROBE_RAM_GB`
    - `UDOS_INSTALLER_PROBE_FREE_STORAGE_GB`
    - `UDOS_INSTALLER_PROBE_HAS_GPU`
    - `UDOS_INSTALLER_PROBE_GPU_VRAM_GB`
  - Added GPU VRAM probing for local-model tier evaluation.
  - Added hardline local-model blocks with explicit reason/remediation fields:
    - `legacy_platform`
    - `insufficient_resources`
  - Added tier-specific resource hardlines:
    - Tier2 requires `>=4 cores`, `>=8GB RAM`, `>=10GB free`
    - Tier3 requires `>=8 cores`, `>=16GB RAM`, `>=50GB free`, `GPU >=8GB VRAM`
  - Updated TinyCore dispatch guard so `--preflight-json` stays in host installer path.

- Added provider fallback policy validation in installer reconcile step:
  - Local backend considered ready only when `ollama` exists and `ollama list` succeeds.
  - Cloud backend considered ready when `MISTRAL_API_KEY` is present.
  - Emits explicit terminal errors and remediation when no provider is available.

- Added test coverage in `core/tests/install_preflight_tier_gates_test.py`:
  - Legacy platform blocks local tier request.
  - Insufficient resources block Tier2 request.
  - Auto tier selects Tier2 for supported host.
  - Auto tier selects Tier3 for capable GPU host.

- Updated installation docs in `docs/INSTALLATION.md`:
  - Added `--preflight-json` usage.
  - Added hardline tier-gate behavior summary.

## Validation Commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  core/tests/install_preflight_tier_gates_test.py \
  core/tests/installer_dispatch_loop_test.py \
  core/tests/installation_guidance_paths_test.py -q
```

## Result

- PASS: `8 passed in 2.36s`
- FAIL: `0`
- WARN: `0`

## Remaining Risk

- Preflight gate logic is validated at installer boundary; full RC1 still requires I3-I7 completion and profile-lane validation.
