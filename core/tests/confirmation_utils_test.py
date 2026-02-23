from __future__ import annotations

from core.input.confirmation_utils import is_help_response, parse_confirmation


def test_is_help_response_accepts_common_help_tokens():
    assert is_help_response("help")
    assert is_help_response("?")
    assert is_help_response("H")


def test_parse_confirmation_skip_variant_choices():
    assert parse_confirmation("1", "yes", "skip") == "yes"
    assert parse_confirmation("0", "yes", "skip") == "no"
    assert parse_confirmation("skip", "yes", "skip") == "skip"
