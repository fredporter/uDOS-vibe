"""One-shot ucode command executor for vibecli integration.

Dispatches a single ucode command in-process (no TUI, no interactive loop)
and returns a rendered output string.  Safe to call via asyncio.to_thread().

Usage::

    from core.tui.ucode_runner import run_ucode_command, format_ucode_result
    result  = run_ucode_command("MAP --list")
    display = format_ucode_result(result)

The :func:`run_ucode_command` function uses the module-level
``CommandDispatcher`` singleton (``core.tui.dispatcher.get_dispatcher``).
The singleton is lazy-initialised on the first call so there is no import-time
cost when vibecli starts.
"""
from __future__ import annotations

import contextlib
import io
from typing import Any

from core.services.logging_manager import get_logger

logger = get_logger("ucode-runner")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_ucode_command(command_text: str) -> dict[str, Any]:
    """Execute a single ucode command and return the handler result dict.

    Uses the global :class:`~core.tui.dispatcher.CommandDispatcher` singleton.
    Any stdout emitted by handlers as a side-effect is captured and attached
    under the ``"stdout"`` key of the returned dict.

    Args:
        command_text: Command string, e.g. ``"HELP"``, ``"MAP --list"``,
                      ``"FIND tokyo"``.

    Returns:
        Handler result dict with at minimum ``{"status": ..., "message": ...}``.
        May include a ``"stdout"`` key if a handler printed to stdout directly.
    """
    # Late imports keep startup cost low and avoid circular-import chains.
    from core.tui.dispatcher import get_dispatcher

    dispatcher = get_dispatcher()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            result = dispatcher.dispatch(command_text)
    except Exception as exc:
        logger.error(f"[ucode-runner] dispatch failed for {command_text!r}: {exc}")
        cmd_word = (
            command_text.strip().split()[0].upper()
            if command_text.strip()
            else ""
        )
        result: dict[str, Any] = {
            "status": "error",
            "command": cmd_word,
            "message": str(exc),
            "recovery_hint": "Run :HEALTH to diagnose the issue",
        }

    # Attach any stdout captured from handler side-effects.
    captured = buf.getvalue()
    if captured:
        result = dict(result)
        result.setdefault("stdout", captured.rstrip())

    return result


def format_ucode_result(result: dict[str, Any]) -> str:
    """Format a handler result dict into a plain display string.

    Uses :class:`~core.tui.renderer.GridRenderer` when available and falls back
    to a compact text representation if the renderer fails.

    Args:
        result: Dict returned by :func:`run_ucode_command`.

    Returns:
        Human-readable string suitable for display in vibecli's message area.
        ANSI escape codes are included (stripped by the Textual widget layer).
    """
    try:
        from core.tui.renderer import GridRenderer

        renderer = GridRenderer()
        rendered = renderer.render(result)
        # Append any captured stdout not already incorporated by the renderer.
        stdout = result.get("stdout", "")
        if stdout and stdout not in rendered:
            rendered = rendered.rstrip() + "\n" + stdout
        return rendered
    except Exception as exc:
        logger.warning(f"[ucode-runner] GridRenderer failed: {exc}")
        # Minimal fallback — never silently swallow the result.
        status = result.get("status", "?").upper()
        message = result.get("message", "")
        stdout = result.get("stdout", "")
        recovery = result.get("recovery_hint", "")
        parts: list[str] = []
        if message:
            parts.append(f"[{status}] {message}")
        else:
            parts.append(f"[{status}]")
        if stdout:
            parts.append(stdout)
        if recovery:
            parts.append(f"→ {recovery}")
        return "\n".join(parts)
