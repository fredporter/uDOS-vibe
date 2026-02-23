# 2026-02-22: uCODE Setup/Token/Cloud stdlib HTTP Segment

## Summary

Refactored core TUI setup/token/cloud networking helpers to use stdlib HTTP path:

- Updated `core/tui/ucode.py` to use:
  - `core.services.stdlib_http.http_get`
  - `core.services.stdlib_http.http_post`
  - `core.services.stdlib_http.HTTPError`
- Replaced `requests` usage in key helper paths:
  - `_get_ok_cloud_status()`
  - setup Wizard submit flow inside `_cmd_setup(...)`
  - `_fetch_or_generate_admin_token()`
  - `_sync_mistral_secret()`
  - `_run_ok_cloud()`
- Preserved behavior for:
  - cloud quota (`429`) handling
  - Wizard offline fallback behavior
  - admin-token generation fallback

## Tests Added

- `core/tests/ucode_setup_network_boundary_test.py`
  - quota mapping for `_run_ok_cloud()` on HTTP 429
  - encoded query shape for `_sync_mistral_secret()`
  - admin-token status fetch path for `_fetch_or_generate_admin_token()`

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/ucode_setup_network_boundary_test.py \
  core/tests/ucode_network_boundary_test.py \
  core/tests/config_sync_network_boundary_test.py \
  core/tests/dev_state_boundary_test.py \
  core/tests/self_healer_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py -q
```

Result: `15 passed`.
