"""uDOS spatial / navigation tools: MAP, GRID, ANCHOR, GOTO, FIND."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import ClassVar

from pydantic import BaseModel, Field

from vibe.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolPermission,
)
from vibe.core.types import ToolStreamEvent

from ._base import _dispatch


# ── Shared result ──────────────────────────────────────────────────────────────

class UcodeResult(BaseModel):
    status: str
    message: str
    data: dict = Field(default_factory=dict)


class UcodeConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS


# ── MAP ────────────────────────────────────────────────────────────────────────

class MapArgs(BaseModel):
    args: str = Field(default="", description="Optional MAP sub-command or flags, e.g. '--full'")


class UcodeMap(BaseTool[MapArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Render the uDOS spatial map view. Shows current location, nearby nodes, "
        "and connected paths. Pass '--full' for an extended view."
    )

    async def run(
        self, args: MapArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"MAP {args.args}".strip()
        result = _dispatch(cmd)
        yield UcodeResult(**_normalise(result))


# ── GRID ───────────────────────────────────────────────────────────────────────

class GridArgs(BaseModel):
    args: str = Field(default="", description="Optional GRID flags, e.g. '--anchors'")


class UcodeGrid(BaseTool[GridArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Display the uDOS grid — the spatial coordinate system. "
        "Shows all registered anchors and their relationships."
    )

    async def run(
        self, args: GridArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"GRID {args.args}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── ANCHOR ─────────────────────────────────────────────────────────────────────

class AnchorArgs(BaseModel):
    action: str = Field(
        default="list",
        description="Action: 'list', 'set <name>', 'remove <name>', or 'go <name>'",
    )


class UcodeAnchor(BaseTool[AnchorArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage spatial anchors — named bookmarks in the uDOS grid. "
        "Actions: list, set, remove, go."
    )

    async def run(
        self, args: AnchorArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"ANCHOR {args.action}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── GOTO ───────────────────────────────────────────────────────────────────────

class GotoArgs(BaseModel):
    destination: str = Field(description="Anchor name or grid coordinate to navigate to")


class UcodeGoto(BaseTool[GotoArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Navigate to a named anchor or grid coordinate in the uDOS spatial system."
    )

    async def run(
        self, args: GotoArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"GOTO {args.destination}")))


# ── FIND ───────────────────────────────────────────────────────────────────────

class FindArgs(BaseModel):
    query: str = Field(description="Search term — location name, tag, or keyword")
    args: str = Field(default="", description="Extra flags, e.g. '--type place'")


class UcodeFind(BaseTool[FindArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Search the uDOS spatial index for locations, anchors, or entities "
        "matching the given query."
    )

    async def run(
        self, args: FindArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"FIND {args.query} {args.args}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── helpers ────────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    """Ensure result always has status/message/data keys."""
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
