"""Command catalog coverage checks against the live dispatcher."""

from __future__ import annotations

from core.services.command_dispatch_service import SUBCOMMAND_ALIASES, UCODE_COMMANDS, match_ucode_command
from core.tui.dispatcher import CommandDispatcher


def test_stage1_ucode_catalog_covers_dispatcher_surface() -> None:
    dispatcher_commands = set(CommandDispatcher().get_command_list())
    assert dispatcher_commands <= UCODE_COMMANDS


def test_legacy_aliases_route_to_canonical_dispatcher_commands() -> None:
    for legacy_command in ("RESTART", "SCHEDULE", "TALK"):
        routed_command, confidence = match_ucode_command(legacy_command)
        assert routed_command == SUBCOMMAND_ALIASES[legacy_command]
        assert confidence == 1.0
