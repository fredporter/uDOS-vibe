# 2026-02-22: Command Surface Canonicalization Segment

## Summary

Continued critical-juncture dispatch consolidation with minimal-change hardening:

- Prompt command surface now auto-registers any missing canonical commands from `core/services/command_catalog.py`.
- Command parity contract test now enforces:
  - contract command set == dispatcher command set
  - canonical command catalog == dispatcher command set
  - prompt command set == dispatcher command set + prompt-local commands (`EXIT`, `OK`)
- Roadmap notes updated to reflect:
  - command-surface canonicalization guardrails are active
  - alias consolidation is partial (remaining ucode-local fuzzy matcher path)

## Files Changed

- `core/input/command_prompt.py`
- `core/tests/command_surface_parity_contract_test.py`
- `docs/roadmap.md`

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/command_surface_parity_contract_test.py \
  core/tests/command_catalog_coverage_test.py \
  core/tests/dispatch_rc_scope_contract_test.py -q
```

Result: `9 passed`.
