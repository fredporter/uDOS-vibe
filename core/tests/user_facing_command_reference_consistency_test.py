"""Consistency checks for user-facing command references in active docs."""

from __future__ import annotations

from pathlib import Path
import re

from core.services.command_dispatch_service import SUBCOMMAND_ALIASES, UCODE_COMMANDS


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_DOCS = [
    REPO_ROOT / "docs" / "roadmap.md",
    REPO_ROOT / "docs" / "howto" / "UCODE-COMMAND-REFERENCE.md",
]


def _extract_backtick_snippets(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def _command_token(snippet: str) -> str | None:
    first = snippet.strip().split(None, 1)[0] if snippet.strip() else ""
    token = first.lstrip("/")
    if not re.fullmatch(r"[A-Z][A-Z0-9]*", token):
        return None
    return token


def test_user_facing_command_tokens_map_to_dispatch_catalog() -> None:
    exclusions = {
        "DOCS",
        "ROADMAP",
        "README",
        "MCP",
        # HTTP methods — valid in API/route documentation, not uDOS commands
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
    }
    known = UCODE_COMMANDS | set(SUBCOMMAND_ALIASES.keys())

    for doc_path in ACTIVE_DOCS:
        snippets = _extract_backtick_snippets(doc_path.read_text(encoding="utf-8"))
        for snippet in snippets:
            token = _command_token(snippet)
            if token is None or token in exclusions:
                continue
            assert token in known, f"{doc_path.name}: unknown command token in snippet `{snippet}`"
