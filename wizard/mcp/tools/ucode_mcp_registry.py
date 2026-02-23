"""Canonical MCP tool registry for uCODE generic and proxy lanes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class MCPToolLane(StrEnum):
    """Ownership lane for MCP tool registration."""

    GENERIC = "generic"
    PROXY = "proxy"


@dataclass(frozen=True, slots=True)
class MCPToolEntry:
    """Canonical MCP tool registration contract entry."""

    name: str
    lane: MCPToolLane
    owner_module: str
    rationale: str


UCODE_MCP_TOOL_REGISTRY: tuple[MCPToolEntry, ...] = (
    MCPToolEntry(
        name="ucode_tools_list",
        lane=MCPToolLane.GENERIC,
        owner_module="wizard.mcp.tools.ucode_tools",
        rationale="Extensibility path: dynamic discovery of all uCODE tools.",
    ),
    MCPToolEntry(
        name="ucode_tools_call",
        lane=MCPToolLane.GENERIC,
        owner_module="wizard.mcp.tools.ucode_tools",
        rationale="Extensibility path: generic invocation for any discovered tool.",
    ),
    MCPToolEntry(
        name="ucode_health",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for high-volume health checks.",
    ),
    MCPToolEntry(
        name="ucode_token",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for auth/token flows.",
    ),
    MCPToolEntry(
        name="ucode_help",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for command help.",
    ),
    MCPToolEntry(
        name="ucode_run",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for run workflows.",
    ),
    MCPToolEntry(
        name="ucode_read",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for read workflows.",
    ),
    MCPToolEntry(
        name="ucode_story",
        lane=MCPToolLane.PROXY,
        owner_module="wizard.mcp.tools.ucode_proxies",
        rationale="Latency/ergonomics path: direct proxy for story workflows.",
    ),
)


def tool_names(lane: MCPToolLane | None = None) -> tuple[str, ...]:
    """Return canonical tool names, optionally filtered by ownership lane."""
    if lane is None:
        return tuple(entry.name for entry in UCODE_MCP_TOOL_REGISTRY)
    return tuple(entry.name for entry in UCODE_MCP_TOOL_REGISTRY if entry.lane == lane)


def tool_registry_records() -> list[dict[str, str]]:
    """Return registry records suitable for docs/debug surfaces."""
    return [{key: str(value) for key, value in asdict(entry).items()} for entry in UCODE_MCP_TOOL_REGISTRY]
