"""uDOS data tools: BINDER, SAVE, LOAD, SEED, MIGRATE, CONFIG."""
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


# ── BINDER ─────────────────────────────────────────────────────────────────────

class BinderArgs(BaseModel):
    action: str = Field(
        description="Action: 'list', 'open <id>', 'create <id>', 'close', 'status'."
    )


class UcodeBinder(BaseTool[BinderArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage uDOS project binders. Each binder is a project workspace with "
        "tasks, calendar events, and completed items. "
        "Actions: list, open, create, close, status."
    )

    async def run(
        self, args: BinderArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"BINDER {args.action}")))


# ── SAVE ───────────────────────────────────────────────────────────────────────

class SaveArgs(BaseModel):
    target: str = Field(
        default="",
        description="What to save: blank for current binder state, or a path/name.",
    )


class UcodeSave(BaseTool[SaveArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Persist the current uDOS state (binder, game state, or named checkpoint) to disk."
    )

    async def run(
        self, args: SaveArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"SAVE {args.target}".strip() if args.target else "SAVE"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── LOAD ───────────────────────────────────────────────────────────────────────

class LoadArgs(BaseModel):
    target: str = Field(
        default="",
        description="What to load: blank for most recent save, or a checkpoint name/path.",
    )


class UcodeLoad(BaseTool[LoadArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Restore uDOS state from disk — most recent save or a named checkpoint."
    )

    async def run(
        self, args: LoadArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"LOAD {args.target}".strip() if args.target else "LOAD"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── SEED ───────────────────────────────────────────────────────────────────────

class SeedArgs(BaseModel):
    action: str = Field(
        default="install",
        description="Action: 'install' (apply seed data), 'status' (check seed state), "
                    "'reset' (re-apply defaults).",
    )


class UcodeSeed(BaseTool[SeedArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage uDOS seed data — the framework defaults that populate vault, memory, "
        "and binder templates on first run."
    )

    async def run(
        self, args: SeedArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"SEED {args.action}")))


# ── MIGRATE ────────────────────────────────────────────────────────────────────

class MigrateArgs(BaseModel):
    direction: str = Field(
        default="up",
        description="Migration direction: 'up' (apply), 'down' (rollback), 'status'.",
    )
    target: str = Field(default="", description="Optional migration target version or name.")


class UcodeMigrate(BaseTool[MigrateArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Run uDOS data migrations — applies schema changes to the local SQLite database "
        "or vault structure."
    )

    async def run(
        self, args: MigrateArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        parts = ["MIGRATE", args.direction]
        if args.target:
            parts.append(args.target)
        yield UcodeResult(**_normalise(_dispatch(" ".join(parts))))


# ── CONFIG ─────────────────────────────────────────────────────────────────────

class ConfigArgs(BaseModel):
    action: str = Field(
        default="show",
        description="Action: 'show', 'get <key>', 'set <key> <value>', 'reset'.",
    )


class UcodeConfig_(BaseTool[ConfigArgs, UcodeResult, UcodeConfig, BaseToolState]):
    """Vibe tool name will be 'ucode_config_' — alias registered below."""

    description: ClassVar[str] = (
        "Read or write uDOS configuration values. "
        "Actions: show (all config), get <key>, set <key> <value>, reset."
    )

    @classmethod
    def get_name(cls) -> str:
        return "ucode_config"

    async def run(
        self, args: ConfigArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"CONFIG {args.action}")))


# ── helpers ────────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
