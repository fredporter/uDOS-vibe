# 2026-02-22: uCODE Matcher Delegation Segment

## Summary

Removed remaining ucode-local fuzzy matcher implementation drift and aligned runtime matching with shared Stage-1 dispatch logic:

- `UCODE._match_ucode_command()` now delegates to `core.services.command_dispatch_service.match_ucode_command`.
- Preserved local short aliases (`?`, `H`, `LS`) as explicit front-door aliases before shared matcher delegation.
- Removed duplicated local Levenshtein implementation from `core/tui/ucode.py`.

This closes the alias/fuzzy matching divergence between:

- `CommandDispatchService` (Stage-1)
- TUI dispatcher normalization paths
- ucode runtime matching

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
  core/tests/dispatch_rc_scope_contract_test.py -q
```

Result: `9 passed`.
