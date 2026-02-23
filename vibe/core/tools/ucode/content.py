"""uDOS content / creative tools: DRAW, SONIC, MUSIC, EMPIRE, DESTROY, UNDO."""
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


# ── DRAW ───────────────────────────────────────────────────────────────────────

class DrawArgs(BaseModel):
    panel: str = Field(
        default="",
        description="Panel name or layout to draw, e.g. 'hud', 'map', 'status'. "
                    "Leave blank for default demo panel.",
    )


class UcodeDraw(BaseTool[DrawArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Render a viewport-aware ASCII panel via uDOS DRAW. "
        "Useful for visualising HUD overlays, map layouts, or status panels."
    )

    async def run(
        self, args: DrawArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"DRAW {args.panel}".strip() if args.panel else "DRAW"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── SONIC ──────────────────────────────────────────────────────────────────────

class SonicArgs(BaseModel):
    action: str = Field(
        default="status",
        description="Action: 'status', 'play <track>', 'stop', 'list'.",
    )


class UcodeSonic(BaseTool[SonicArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Control uDOS SONIC — the ambient sound / audio cue system. "
        "Actions: status, play, stop, list."
    )

    async def run(
        self, args: SonicArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"SONIC {args.action}")))


# ── MUSIC ──────────────────────────────────────────────────────────────────────

class MusicArgs(BaseModel):
    action: str = Field(
        default="status",
        description="Action: 'status', 'play <playlist>', 'stop', 'next', 'list'.",
    )


class UcodeMusic(BaseTool[MusicArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Control uDOS MUSIC — background music / playlist management. "
        "Actions: status, play, stop, next, list."
    )

    async def run(
        self, args: MusicArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"MUSIC {args.action}")))


# ── EMPIRE ─────────────────────────────────────────────────────────────────────

class EmpireArgs(BaseModel):
    action: str = Field(
        default="status",
        description="Action: 'status', 'build <node>', 'expand', 'report'.",
    )


class UcodeEmpire(BaseTool[EmpireArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Manage the uDOS Empire — the multi-node wizard network. "
        "View status, build nodes, or expand the empire's reach."
    )

    async def run(
        self, args: EmpireArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"EMPIRE {args.action}")))


# ── DESTROY ────────────────────────────────────────────────────────────────────

class DestroyArgs(BaseModel):
    target: str = Field(
        description="What to destroy: 'cache', 'logs', 'binder <id>', or '--all' (requires confirm)."
    )
    confirm: bool = Field(
        default=False,
        description="Set to true to confirm destructive operations.",
    )


class UcodeDestroy(
    BaseTool[DestroyArgs, UcodeResult, UcodeConfig, BaseToolState]
):
    description: ClassVar[str] = (
        "Destroy / wipe uDOS data. Targets: cache, logs, a specific binder, or --all. "
        "Requires confirm=true for destructive operations."
    )

    @classmethod
    def get_name(cls) -> str:  # avoid collision with built-in naming
        return "ucode_destroy"

    async def run(
        self, args: DestroyArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        if not args.confirm and args.target == "--all":
            yield UcodeResult(
                status="error",
                message="confirm=true required to run DESTROY --all",
                data={},
            )
            return
        flags = "--confirm" if args.confirm else ""
        cmd = f"DESTROY {args.target} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── UNDO ───────────────────────────────────────────────────────────────────────

class UndoArgs(BaseModel):
    steps: int = Field(default=1, ge=1, le=10, description="Number of steps to undo (1–10).")


class UcodeUndo(BaseTool[UndoArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Undo the last N uDOS actions by restoring from the most recent backup snapshot."
    )

    async def run(
        self, args: UndoArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"UNDO {args.steps}" if args.steps > 1 else "UNDO"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── STORY ──────────────────────────────────────────────────────────────────────

class StoryArgs(BaseModel):
    action: str = Field(
        default="list",
        description="Action: 'list' (show available), 'read <id>' (read story), "
                    "'resume <id>' (continues reading), 'status' (show active).",
    )


class UcodeStory(BaseTool[StoryArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Interact with narrative content stored in the vault. "
        "Read, navigate, and explore branching stories and interactive fiction."
    )

    async def run(
        self, args: StoryArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        yield UcodeResult(**_normalise(_dispatch(f"STORY {args.action}")))


# ── TALK ───────────────────────────────────────────────────────────────────────

class TalkArgs(BaseModel):
    target: str = Field(
        description="NPC or character to talk to, e.g. 'guide', 'merchant', 'sage'."
    )
    message: str = Field(
        default="",
        description="Optional message or question to ask the NPC.",
    )


class UcodeTalk(BaseTool[TalkArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Interact with NPCs and characters in the uDOS world. "
        "Ask questions, trade, or have conversations that affect gameplay."
    )

    async def run(
        self, args: TalkArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"TALK {args.target} {args.message}".strip() if args.message else f"TALK {args.target}"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── READ ───────────────────────────────────────────────────────────────────────

class ReadArgs(BaseModel):
    path: str = Field(
        description="File or path to read, e.g. 'docs/guide.md', 'vault/notes/project-x'."
    )
    section: str = Field(
        default="",
        description="Optional section/heading to show, e.g. 'Installation', 'Troubleshooting'.",
    )


class UcodeRead(BaseTool[ReadArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Read and display markdown or text content from the vault or documentation. "
        "Supports filtering by section and pretty-printing with formatting."
    )

    async def run(
        self, args: ReadArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        cmd = f"READ {args.path} --section {args.section}".strip() if args.section else f"READ {args.path}"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── PLAY ───────────────────────────────────────────────────────────────────────

class PlayArgs(BaseModel):
    game: str = Field(
        default="",
        description="Game to play: 'adventure', 'roguelike', 'puzzle', 'empire'. "
                    "Empty for list of available games.",
    )
    action: str = Field(
        default="start",
        description="Game action: 'start' (new game), 'continue' (resume), 'status' (show state).",
    )


class UcodePlay(BaseTool[PlayArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Play interactive games within uDOS. Adventure games, roguelikes, puzzles, "
        "and more. Track progress in your binder and save/load states."
    )

    async def run(
        self, args: PlayArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        if args.game:
            cmd = f"PLAY {args.game} --action {args.action}"
        else:
            cmd = "PLAY"
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── PRINT ──────────────────────────────────────────────────────────────────────

class PrintArgs(BaseModel):
    content: str = Field(
        description="Content to print/output, or path to file."
    )
    format: str = Field(
        default="auto",
        description="Output format: 'auto', 'markdown', 'plain', 'json', 'table'.",
    )
    page: bool = Field(
        default=True,
        description="Use pager for long output.",
    )


class UcodePrint(BaseTool[PrintArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Format and output content with styling. Supports markdown, JSON, tables, "
        "and other formats. Useful for displaying results in readable ways."
    )

    async def run(
        self, args: PrintArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--format {args.format}" if args.format != "auto" else ""
        flags += " --pager" if args.page else ""
        cmd = f"PRINT {args.content} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── FORMAT ─────────────────────────────────────────────────────────────────────

class FormatArgs(BaseModel):
    input: str = Field(
        description="Content to format, or path to file."
    )
    style: str = Field(
        default="json",
        description="Target style: 'json', 'yaml', 'toml', 'markdown', 'csv'.",
    )
    compact: bool = Field(
        default=False,
        description="Compact output (no pretty-printing).",
    )


class UcodeFormat(BaseTool[FormatArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Convert and format data between different styles (JSON, YAML, TOML, CSV, etc.). "
        "Validates syntax and reformats for consistency."
    )

    async def run(
        self, args: FormatArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--style {args.style}" if args.style else ""
        flags += " --compact" if args.compact else ""
        cmd = f"FORMAT {args.input} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── helpers ────────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
