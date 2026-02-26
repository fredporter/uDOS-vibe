"""Unit tests for core.tui.ucode_runner.

Verifies that the one-shot executor dispatches commands correctly and that
format_ucode_result produces non-empty strings for both success and error
results.
"""
from __future__ import annotations

import pytest

from core.tui.ucode_runner import format_ucode_result, run_ucode_command


class TestRunUcodeCommand:
    """Tests for run_ucode_command()."""

    def test_returns_dict(self):
        result = run_ucode_command("HELP")
        assert isinstance(result, dict)

    def test_help_returns_success(self):
        result = run_ucode_command("HELP")
        assert result.get("status") == "success"

    def test_help_has_commands_key(self):
        result = run_ucode_command("HELP")
        # HELP handler populates "commands" with the catalog.
        assert "commands" in result or "help" in result or "message" in result

    def test_status_returns_success(self):
        result = run_ucode_command("STATUS")
        assert result.get("status") in {"success", "warning"}

    def test_health_returns_a_result(self):
        result = run_ucode_command("HEALTH")
        assert "status" in result

    def test_unknown_command_returns_error(self):
        result = run_ucode_command("ZZZNOPE")
        assert result.get("status") == "error"

    def test_empty_command_returns_error(self):
        result = run_ucode_command("")
        assert result.get("status") == "error"

    def test_result_always_has_status(self):
        for cmd in ("HELP", "STATUS", "HEALTH", "ZZZBAD"):
            result = run_ucode_command(cmd)
            assert "status" in result, f"Missing 'status' for command {cmd!r}"

    def test_subcommand_alias_resolves(self):
        """STAT and STATE are aliases for STATUS in the catalog."""
        result = run_ucode_command("STAT")
        assert result.get("status") in {"success", "warning"}


class TestFormatUcodeResult:
    """Tests for format_ucode_result()."""

    def test_success_result_returns_nonempty_string(self):
        result = run_ucode_command("HELP")
        formatted = format_ucode_result(result)
        assert isinstance(formatted, str)
        assert formatted.strip()

    def test_error_result_returns_nonempty_string(self):
        result = run_ucode_command("ZZZNOPE")
        formatted = format_ucode_result(result)
        assert isinstance(formatted, str)
        assert formatted.strip()

    def test_minimal_result_does_not_crash(self):
        """format_ucode_result must handle minimal dicts gracefully."""
        for minimal in (
            {"status": "success"},
            {"status": "error", "message": "oops"},
            {},
        ):
            out = format_ucode_result(minimal)
            assert isinstance(out, str)

    def test_stdout_included_in_output(self):
        """If a handler emitted stdout, it appears in the formatted output."""
        result = {"status": "success", "message": "ok", "stdout": "extra output line"}
        formatted = format_ucode_result(result)
        assert "extra output line" in formatted
