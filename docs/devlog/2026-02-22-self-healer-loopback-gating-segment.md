# 2026-02-22: Self-Healer Loopback Gating Segment

## Summary

Extended core networking boundary enforcement in Self-Healer:

- `core/services/self_healer.py`
  - `_check_ollama()` now uses structured host sanitization instead of string prefix checks.
  - added `_sanitize_loopback_ollama_host(raw_host)`:
    - allows only loopback hosts (`127.0.0.1`, `::1`, `localhost`)
    - normalizes host output to `{scheme}://{hostname}:{port}`
    - blocks non-loopback values by returning empty string (no remote auto-heal probe)

## Tests Added

- `core/tests/self_healer_boundary_test.py`
  - loopback Ollama host accepted
  - non-loopback Ollama host rejected

## Validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin \
  -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot \
  core/tests/self_healer_boundary_test.py \
  core/tests/ucode_network_boundary_test.py \
  core/tests/config_sync_network_boundary_test.py \
  core/tests/dev_state_boundary_test.py \
  core/tests/core_network_boundary_contract_test.py -q
```

Result: `12 passed`.
