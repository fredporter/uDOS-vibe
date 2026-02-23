"""uDOS workspace tools: PLACE, SCHEDULER, SCRIPT, USER."""
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


# ── PLACE ──────────────────────────────────────────────────────────────────────

class PlaceArgs(BaseModel):
    action: str = Field(
        description="Action: 'list', 'open <name>', 'create <name>', 'switch <name>'."
    )


class UcodePlace(BaseTool[PlaceArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage uDOS workspace places — named working contexts that group files, "
        "binders, and settings. Actions: list, open, create, switch."
    )

    async def run(
        self, args: PlaceArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"PLACE {args.action}")))


# ── SCHEDULER ──────────────────────────────────────────────────────────────────

class SchedulerArgs(BaseModel):
    action: str = Field(
        default="list",
        description="Action: 'list', 'add <cron> <command>', 'remove <id>', 'run <id>'.",
    )


class UcodeScheduler(BaseTool[SchedulerArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage the uDOS task scheduler. Schedule recurring commands using cron syntax. "
        "Actions: list, add, remove, run."
    )

    async def run(
        self, args: SchedulerArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"SCHEDULER {args.action}")))


# ── SCRIPT ─────────────────────────────────────────────────────────────────────

class ScriptArgs(BaseModel):
    action: str = Field(
        description="Action: 'list', 'run <name>', 'show <name>', 'edit <name>'."
    )


class UcodeScript(BaseTool[ScriptArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Execute or manage uDOS system scripts — pre-defined automation sequences "
        "stored in the vault. Actions: list, run, show, edit."
    )

    async def run(
        self, args: ScriptArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"SCRIPT {args.action}")))


# ── USER ───────────────────────────────────────────────────────────────────────

class UserArgs(BaseModel):
    action: str = Field(
        default="show",
        description="Action: 'show', 'list', 'create <username>', 'switch <username>', "
                    "'permissions <username>'.",
    )


class UcodeUser(BaseTool[UserArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage uDOS user profiles and permissions. "
        "Actions: show (current user), list, create, switch, permissions."
    )

    async def run(
        self, args: UserArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"USER {args.action}")))


# ── SETUP ──────────────────────────────────────────────────────────────────────

class SetupArgs(BaseModel):
    step: str = Field(
        default="wizard",
        description="Setup step: 'wizard' (interactive), 'quick' (defaults), "
                    "'config' (settings), 'validate' (verify).",
    )
    confirm: bool = Field(
        default=False,
        description="Skip confirmation prompts.",
    )


class UcodeSetup(BaseTool[SetupArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Run the uDOS setup wizard. Guides through environment initialization, "
        "dependency installation, vault seeding, and health checks."
    )

    async def run(
        self, args: SetupArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = "--yes" if args.confirm else ""
        cmd = f"SETUP {args.step} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── RUN ────────────────────────────────────────────────────────────────────────

class RunArgs(BaseModel):
    script: str = Field(
        description="Script name or path to execute, e.g. 'backup', 'sync', './scripts/migrate.sh'."
    )
    args: str = Field(
        default="",
        description="Arguments to pass to the script.",
    )
    dry_run: bool = Field(
        default=False,
        description="Show what would run without executing.",
    )


class UcodeRun(BaseTool[RunArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Execute a uDOS automation script or shell command. "
        "Can run built-in scripts or user-defined scripts from the workspace."
    )

    async def run(
        self, args: RunArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = "--dry-run" if args.dry_run else ""
        cmd = f"RUN {args.script} {args.args} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── helpers ────────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
