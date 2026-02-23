"""Command examples in active docs should resolve through dispatcher stage 1."""

from __future__ import annotations

from core.services.command_dispatch_service import match_ucode_command


DOC_COMMAND_EXAMPLES = [
    ("UCODE DEMO LIST", "UCODE"),
    ("UCODE DEMO RUN sample-script", "UCODE"),
    ("UCODE SYSTEM INFO", "UCODE"),
    ("UCODE DOCS networking", "UCODE"),
    ("UCODE UPDATE", "UCODE"),
    ("UCODE CAPABILITIES --filter wizard", "UCODE"),
    ("UCODE PLUGIN INSTALL sample-plugin", "UCODE"),
    ("UCODE METRICS", "UCODE"),
    ("MODE STATUS", "MODE"),
    ("MODE THEME cyberpunk", "MODE"),
    ("PLAY LENS", "PLAY"),
    ("PLAY LENS SCORE elite --compact", "PLAY"),
    ("PLAY PROFILE STATUS --group alpha --session run-1", "PLAY"),
    ("FILE SELECT --file README.md", "FILE"),
]


def test_active_docs_command_examples_route_to_expected_ucode_commands() -> None:
    for raw_command, expected in DOC_COMMAND_EXAMPLES:
        command, confidence = match_ucode_command(raw_command)
        assert command == expected
        assert confidence >= 0.8
