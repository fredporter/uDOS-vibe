# 2026-02-22: Dispatch Ownership Consolidation Segment

## Summary

Consolidated remaining parallel dispatch behavior in `core/tui/ucode.py`:

- Removed legacy local three-stage path:
  - deleted `_validate_shell_syntax()`
  - deleted `_dispatch_three_stage()`
- Updated compatibility entrypoint:
  - `_handle_question_mode()` now delegates to canonical `_dispatch_with_vibe()`
- Kept matcher alignment from earlier segment:
  - `_match_ucode_command()` delegates to shared Stage-1 matcher

This removes duplicate runtime routing logic and keeps one canonical dispatch flow in TUI runtime.

## Files Changed

- `core/tui/ucode.py`
- `core/tests/ucode_alias_matcher_contract_test.py`
- `docs/roadmap.md`

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/ucode_alias_matcher_contract_test.py \
  core/tests/command_surface_parity_contract_test.py \
  core/tests/dispatch_rc_scope_contract_test.py \
  core/tests/vibe_dispatch_adapter_test.py -q
```

Result: `35 passed`.
