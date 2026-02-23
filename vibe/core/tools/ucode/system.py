"""uDOS system tools: HEALTH, VERIFY, REPAIR, UID, TOKEN, VIEWPORT."""
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


class UcodeResult(BaseModel):
    status: str
    message: str
    data: dict = Field(default_factory=dict)


class UcodeConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS


# ── HEALTH ─────────────────────────────────────────────────────────────────────

class HealthArgs(BaseModel):
    check: str = Field(
        default="",
        description="Optional subsystem to check, e.g. 'db', 'wizard', 'vault'. "
                    "Leave blank for a full health report.",
    )


class UcodeHealth(BaseTool[HealthArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Run a uDOS health check. Reports the status of all subsystems "
        "(database, vault, wizard, memory, etc.). Optionally target a specific subsystem."
    )

    async def run(
        self, args: HealthArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"HEALTH {args.check}".strip() if args.check else "HEALTH"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── VERIFY ─────────────────────────────────────────────────────────────────────

class VerifyArgs(BaseModel):
    target: str = Field(
        default="",
        description="What to verify: 'install', 'config', 'vault', or blank for all.",
    )


class UcodeVerify(BaseTool[VerifyArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Verify the uDOS installation integrity — checks config files, dependencies, "
        "and vault structure. Use before reporting issues."
    )

    async def run(
        self, args: VerifyArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"VERIFY {args.target}".strip() if args.target else "VERIFY"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── REPAIR ─────────────────────────────────────────────────────────────────────

class RepairArgs(BaseModel):
    action: str = Field(
        default="",
        description="Repair action: '--install' (deps), '--config' (reset config), "
                    "'--vault' (seed missing vault files), or blank for auto-detect.",
    )


class UcodeRepair(BaseTool[RepairArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Self-heal the uDOS installation. Can reinstall dependencies, reset config, "
        "or restore missing vault files. Safe to run at any time."
    )

    async def run(
        self, args: RepairArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"REPAIR {args.action}".strip() if args.action else "REPAIR"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── UID ────────────────────────────────────────────────────────────────────────

class UidArgs(BaseModel):
    action: str = Field(
        default="show",
        description="Action: 'show' (current UID), 'generate' (new UID), 'rotate'.",
    )


class UcodeUid(BaseTool[UidArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage the uDOS user/device UID. Show the current UID or generate a new one."
    )

    async def run(
        self, args: UidArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"UID {args.action}")))


# ── TOKEN ──────────────────────────────────────────────────────────────────────

class TokenArgs(BaseModel):
    action: str = Field(
        default="show",
        description="Action: 'show', 'generate', 'revoke', or 'list'.",
    )
    name: str = Field(default="", description="Token name (for generate/revoke).")


class UcodeToken(BaseTool[TokenArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage uDOS access tokens — generate, list, or revoke tokens used for "
        "wizard API authentication."
    )

    async def run(
        self, args: TokenArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        parts = ["TOKEN", args.action]
        if args.name:
            parts.append(args.name)
        yield UcodeResult(**_normalise(_dispatch(" ".join(parts))))


# ── VIEWPORT ───────────────────────────────────────────────────────────────────

class ViewportArgs(BaseModel):
    args: str = Field(default="", description="Optional VIEWPORT flags.")


class UcodeViewport(BaseTool[ViewportArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Report the current terminal/viewport dimensions (rows × cols) as seen by uDOS. "
        "Useful for layout-aware tool output."
    )

    async def run(
        self, args: ViewportArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"VIEWPORT {args.args}".strip() if args.args else "VIEWPORT"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── HELP ────────────────────────────────────────────────────────────────────────

class HelpArgs(BaseModel):
    command: str = Field(
        default="",
        description="Command to get help for, e.g. 'HEALTH', 'BINDER', 'MAP'. "
                    "Leave blank for a list of all available commands.",
    )
    topic: str = Field(
        default="",
        description="Optional topic to search, e.g. 'navigation', 'data', 'system'.",
    )


class UcodeHelp(BaseTool[HelpArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Get help with uDOS commands. List all available commands, or get detailed help "
        "for a specific command. Topics include system, navigation, data, workspace, creative."
    )

    async def run(
        self, args: HelpArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        if args.command:
            cmd = f"HELP {args.command}"
        elif args.topic:
            cmd = f"HELP --topic {args.topic}"
        else:
            cmd = "HELP"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── helpers ────────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
