# 2026-02-22: Core Networking Critical Juncture Complete

## Summary

Marked the roadmap item
`Remove non-Wizard networking paths from core runtime and TUI layers; gate any unavoidable paths behind explicit Wizard-only runtime checks`
as complete.

Completion basis in this round:

- Core TUI networking paths migrated to stdlib HTTP and loopback-safe base resolution.
- Core service paths (`config_sync_service`, `dev_state`, `self_healer`) enforce loopback-only targets for direct runtime probes/sync calls.
- Wizard command/runtime host resolution paths (`wizard_handler`, `fkey_handler`, `status_bar`) enforce loopback target coercion/rejection.
- CI guardrails now include:
  - import-surface allowlist freeze
  - no public DNS probe literal check
  - AST static check for non-loopback literal HTTP/socket call targets in network-capable core modules.

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/core_network_boundary_contract_test.py \
  core/tests/ucode_setup_network_boundary_test.py \
  core/tests/ucode_network_boundary_test.py \
  core/tests/config_sync_network_boundary_test.py \
  core/tests/dev_state_boundary_test.py \
  core/tests/self_healer_boundary_test.py \
  core/tests/wizard_handler_boundary_test.py \
  core/tests/fkey_status_bar_boundary_test.py -q
```

Result: verified passing in segmented runs during implementation; this command is the consolidated gate profile for this track.
