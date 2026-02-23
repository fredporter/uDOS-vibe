"""
uDOS tools — Phase B+ MCP-only (no Phase A fallback).

All tool invocations go through the Vibe MCP server (wizard/mcp/mcp_server.py)
configured in .vibe/config.toml. These BaseTool subclasses are auto-discovered
by Vibe and proxied through MCP.

Phase A (offline CommandDispatcher) has been removed. Tools no longer have
a direct fallback path; they always use MCP.
"""
from __future__ import annotations

from typing import Any


def _dispatch(command: str, **_: Any) -> dict[str, Any]:
    """
    Placeholder: Phase A offline path removed.

    All tool calls now go through Vibe MCP server (wizard/mcp/mcp_server.py).
    This function should never be called in production; it exists only to
    prevent import errors during tool discovery.

    Raises:
        RuntimeError: Phase A offline fallback is not available.
    """
    raise RuntimeError(
        "Phase A offline fallback removed. "
        "Tools must use Vibe MCP server (wizard/mcp/mcp_server.py). "
        "Ensure .vibe/config.toml is valid and MCP server is running."
    )
