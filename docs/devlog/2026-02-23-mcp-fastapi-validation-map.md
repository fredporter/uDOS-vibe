# MCP FastAPI Validation Map (Cycle D)

Date: 2026-02-23
Scope: `wizard/tests/test_mcp_server.py` under FastAPI-enabled profile

## Test to Contract Mapping

- `test_load_tool_index_reads_tools` -> `wizard/mcp/mcp_server.py:_load_tool_index` parses canonical tool docs (`api/wizard/tools/mcp-tools.md`).
- `test_load_tool_index_fallback_docs_path` -> `wizard/mcp/mcp_server.py:_load_tool_index` fallback path (`wizard/docs/api/tools/mcp-tools.md`).
- `test_load_tool_index_normalizes_dotted_tool_names` -> `wizard/mcp/mcp_server.py:_load_tool_index` dotted-name normalization (`.` -> `_`).
- `test_wizard_tools_list_uses_index` -> `wizard/mcp/mcp_server.py:wizard_tools_list` response contract `{count, tools}` backed by `_load_tool_index`.
- `test_wizard_tools_registration_status` -> `wizard/mcp/mcp_server.py:wizard_tools_registration_status` + `_tool_registration_protocol` indexed/server diff contract.
- `test_wizard_tools_registration_status_applies_aliases_and_filters_non_tool_tokens` -> `wizard/mcp/mcp_server.py:TOOL_INDEX_ALIASES` + `_tool_registration_protocol` alias normalization and filtering.
- `test_enforce_mcp_security_requires_admin_token` -> `wizard/mcp/mcp_server.py:_enforce_mcp_security` admin-token gate (`WIZARD_MCP_REQUIRE_ADMIN_TOKEN`, `WIZARD_ADMIN_TOKEN`).
- `test_enforce_mcp_security_per_minute_limit` -> `wizard/mcp/mcp_server.py:_enforce_mcp_security` per-minute rate-limit gate (`WIZARD_MCP_RATE_LIMIT_PER_MIN`).
- `test_enforce_mcp_security_cooldown_active` -> `wizard/mcp/mcp_server.py:_enforce_mcp_security` minimum-interval cooldown gate (`WIZARD_MCP_MIN_INTERVAL_SECONDS`).
- `test_mcp_limits_invalid_env_falls_back_to_defaults` -> `wizard/mcp/mcp_server.py:_mcp_limits` malformed env fallback to safe defaults.
- `test_extract_ucode_output_prefers_result` -> `wizard/mcp/mcp_server.py:_extract_ucode_output` precedence for nested result payload.
- `test_extract_ucode_output_handles_rendered` -> `wizard/mcp/mcp_server.py:_extract_ucode_output` `rendered` fallback branch.
- `test_extract_ucode_output_handles_string_input` -> `wizard/mcp/mcp_server.py:_extract_ucode_output` non-dict passthrough.
- `test_wrap_display_includes_all_sections` -> `wizard/mcp/mcp_server.py:_wrap_display` display composition (status/emoji/toolbar/content).
- `test_ucode_command_wraps_display` -> `wizard/mcp/mcp_server.py:ucode_command` MCP tool output wrapping contract.
- `test_mcp_server_has_expected_tools` -> `wizard/mcp/mcp_server.py:mcp` tool registration presence for core tool surface.
- `test_load_tool_index_ignores_malformed_and_noncanonical_tokens` -> `wizard/mcp/mcp_server.py:_load_tool_index` strict markdown-bullet parsing and token hygiene.

## Observed Weak Spots

- Remaining weak spots are primarily around operational behavior (network/service availability) rather than parser/security branch coverage.

## Current Validation Result

- Targeted run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot wizard/tests/test_mcp_server.py`
- Result: all MCP server tests passed (17/17).
