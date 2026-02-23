# 2026-02-23 I1: Minimum Spec Parity Validation Pass

## Scope

Complete I1 from `docs/roadmap.md`: minimum spec parity validation and test refresh for offline/online uCODE pathways.

## Changes

- Updated offline fallback order in `core/commands/ucode_handler.py` to include capability checks:
  - `UCODE DEMO LIST`
  - `UCODE DOCS --query <text>`
  - `UCODE SYSTEM INFO`
  - `UCODE CAPABILITIES --filter <text>`
- Updated first-run offline launcher hint in `core/tui/ucode.py` to match the same deterministic order.
- Refreshed fallback-order assertion in `core/tests/ucode_min_spec_command_test.py`.
- Added startup guidance coverage in `core/tests/ucode_startup_offline_hint_test.py`.
- Synced docs to the validated behavior:
  - `docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md`
  - `docs/howto/UCODE-COMMAND-REFERENCE.md`

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
  core/tests/ucode_min_spec_command_test.py \
  core/tests/ucode_entrypoint_test.py \
  core/tests/docs_command_examples_contract_test.py \
  core/tests/ucode_startup_offline_hint_test.py -q
```

## Result

- PASS: `21 passed in 2.04s`
- FAIL: `0`
- WARN: `0`

## Remaining Risk

- This I1 validation is targeted (uCODE parity + startup hints + command examples).
- Full RC1 closeout still requires profile-lane validation and completion of I2-I7 milestone items.
