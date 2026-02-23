# Wizard MCP Gateway

This directory hosts the canonical Wizard MCP stdio server used by Vibe.

## Canonical Entry Point

- Runtime: `wizard/mcp/mcp_server.py`
- Activation manager: `scripts/mcp_activation.py`

## Single Activation Path (Cross-Platform)

```bash
uv run --project . scripts/mcp_activation.py <enable|disable|status|contract>
```

The script manages only the marked block in `.vibe/config.toml`:

- `# BEGIN UCODE MANAGED MCP (WIZARD)`
- `# END UCODE MANAGED MCP (WIZARD)`

## Quick Runtime Checks

```bash
uv run --project . wizard/mcp/mcp_server.py --tools
uv run --project . wizard/mcp/mcp_server.py --ucode "STATUS"
```

## Notes

- `gateway.py` is the HTTP client bridge used by MCP tools.
- Tool index docs are read from `api/wizard/tools/mcp-tools.md` with fallback to `wizard/docs/api/tools/mcp-tools.md`.
