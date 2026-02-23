from core.services.command_catalog import (
    parse_slash_command,
    resolve_allowlisted_slash_command,
)


def test_parse_slash_command_returns_none_for_non_slash_input() -> None:
    assert parse_slash_command("HELP") is None


def test_parse_slash_command_tokenizes_and_normalizes_first_token() -> None:
    parsed = parse_slash_command("/help topic")
    assert parsed is not None
    assert parsed.body == "help topic"
    assert parsed.first_token == "HELP"
    assert parsed.rest == "topic"
    assert parsed.normalized_ucode_command == "HELP topic"


def test_resolve_allowlisted_slash_command_is_case_insensitive() -> None:
    parsed = parse_slash_command("/help")
    assert parsed is not None
    assert resolve_allowlisted_slash_command(parsed, {"help"}) == "HELP"
