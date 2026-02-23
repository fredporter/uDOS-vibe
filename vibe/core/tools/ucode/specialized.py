"""uDOS specialized tools: WATCH, EXPORT, IMPORT, NOTIFY, BENCH."""
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


# ── WATCH ──────────────────────────────────────────────────────────────────

class WatchArgs(BaseModel):
    path: str = Field(
        description="Path to watch for changes, e.g. 'vault/', './src/'."
    )
    patterns: str = Field(
        default="*",
        description="File patterns to watch, e.g. '*.py', '*.md', comma-separated.",
    )
    action: str = Field(
        default="monitor",
        description="Action: 'start' (begin watching), 'stop' (stop), 'status' (check).",
    )
    callback: str = Field(
        default="",
        description="Optional callback command to run on file change.",
    )


class UcodeWatch(BaseTool[WatchArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Watch a directory for file changes. Useful for triggering automation "
        "on file modifications. Can run callbacks on change events."
    )

    async def run(
        self, args: WatchArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--patterns {args.patterns}" if args.patterns != "*" else ""
        if args.callback:
            flags += f" --callback {args.callback}"
        cmd = f"WATCH {args.path} {args.action} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── EXPORT ─────────────────────────────────────────────────────────────────

class ExportArgs(BaseModel):
    source: str = Field(
        description="What to export: 'vault', 'binder <id>', 'logs', 'config'."
    )
    format: str = Field(
        default="zip",
        description="Export format: 'zip', 'tar', 'json', 'csv', 'backup'.",
    )
    output: str = Field(
        default="",
        description="Output path. If empty, uses default location.",
    )
    compress: bool = Field(
        default=True,
        description="Compress output.",
    )


class UcodeExport(BaseTool[ExportArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Export vault, binders, logs, or configuration in various formats. "
        "Useful for backup, sharing, or migration."
    )

    async def run(
        self, args: ExportArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--format {args.format}" if args.format else ""
        if args.output:
            flags += f" --output {args.output}"
        if not args.compress:
            flags += " --no-compress"
        cmd = f"EXPORT {args.source} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── IMPORT ─────────────────────────────────────────────────────────────────

class ImportArgs(BaseModel):
    source: str = Field(
        description="Source file or path to import from."
    )
    target: str = Field(
        default="vault",
        description="Where to import: 'vault', 'binder <id>', 'config'.",
    )
    merge: bool = Field(
        default=True,
        description="Merge with existing data (vs. replace).",
    )
    validate_input: bool = Field(
        default=True,
        alias="validate",
        description="Validate data during import.",
    )


class UcodeImport(BaseTool[ImportArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Import data from backup files, exports, or other sources. "
        "Supports various formats and smart validation."
    )

    async def run(
        self, args: ImportArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--target {args.target}" if args.target else ""
        if not args.merge:
            flags += " --replace"
        if not args.validate_input:
            flags += " --no-validate"
        cmd = f"IMPORT {args.source} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── NOTIFY ────────────────────────────────────────────────────────────────

class NotifyArgs(BaseModel):
    level: str = Field(
        default="info",
        description="Notification level: 'info', 'success', 'warning', 'error'.",
    )
    message: str = Field(
        description="Notification message to display.",
    )
    channels: str = Field(
        default="console",
        description="Where to send: 'console', 'email', 'webhook', comma-separated.",
    )
    persist: bool = Field(
        default=False,
        description="Persist notification in history.",
    )


class UcodeNotify(BaseTool[NotifyArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Send notifications to various channels (console, email, webhooks). "
        "Useful for alerting on important events."
    )

    async def run(
        self, args: NotifyArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--level {args.level}" if args.level else ""
        if args.channels != "console":
            flags += f" --channels {args.channels}"
        if args.persist:
            flags += " --persist"
        cmd = f'NOTIFY "{args.message}" {flags}'.strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── BENCH ──────────────────────────────────────────────────────────────────

class BenchArgs(BaseModel):
    target: str = Field(
        description="What to benchmark: 'system', 'vault', 'io', 'search', 'all'."
    )
    iterations: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of iterations (1-1000).",
    )
    output: str = Field(
        default="console",
        description="Output format: 'console', 'json', 'report'.",
    )


class UcodeBench(BaseTool[BenchArgs, UcodeResult, UcodeConfig, BaseToolState]):
    description: ClassVar[str] = (
        "Benchmark uDOS components for performance analysis. "
        "Tests system, I/O, search, and vault operations."
    )

    async def run(
        self, args: BenchArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | UcodeResult, None]:
        flags = f"--iterations {args.iterations}" if args.iterations != 10 else ""
        if args.output != "console":
            flags += f" --output {args.output}"
        cmd = f"BENCH {args.target} {flags}".strip()
        yield UcodeResult(**_normalise(_dispatch(cmd)))


# ── helpers ────────────────────────────────────────────────────────────────

def _normalise(raw: dict) -> dict:
    return {
        "status": raw.get("status", "ok"),
        "message": raw.get("message", ""),
        "data": {k: v for k, v in raw.items() if k not in {"status", "message"}},
    }
