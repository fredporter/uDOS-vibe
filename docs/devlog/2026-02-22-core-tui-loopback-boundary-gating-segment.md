# 2026-02-22: Core TUI Loopback Boundary Gating Segment

## Summary

Advanced the critical-juncture networking cleanup by enforcing loopback-only behavior in core TUI networking surfaces:

- Added URL boundary sanitizer in `UCODE`:
  - `_resolve_loopback_url(url, fallback, context)`
  - non-loopback hosts are blocked and replaced with loopback fallback
- Applied sanitizer to:
  - `_wizard_base_url()` (from `WIZARD_BASE_URL`)
  - `_get_ok_local_status()` (`ollama_endpoint` from mode config)
  - `_fetch_ollama_models()` endpoint usage
  - setup sync path base URL resolution (now uses `_wizard_base_url()`)
- Added class-level loopback host allowlist:
  - `127.0.0.1`, `::1`, `localhost`

## Files Changed

- `core/tui/ucode.py`
- `core/tests/ucode_network_boundary_test.py`
- `docs/roadmap.md`

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/ucode_network_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py \
  core/tests/ucode_alias_matcher_contract_test.py \
  core/tests/web_home_proxy_handler_test.py -q
```

Result: `15 passed`.

## Remaining Scope

This does not fully complete the roadmap networking item. Remaining work includes eliminating or gating other direct networking usage across additional core modules (for example setup/config/self-heal surfaces) behind explicit loopback/wizard boundary contracts.
