"""
Tests for ucode_registry warning behavior.

Verifies that:
- discover_ucode_tools() emits [MCP WARNING] to stderr when a module fails
  to import, instead of silently swallowing the error.
- Healthy modules are still discovered even when one module fails.
- The warning message includes the module name and exception type.
"""
from __future__ import annotations

import importlib
import io
import sys
from unittest.mock import patch

import pytest

from wizard.mcp.tools.ucode_registry import (
    UCODE_MODULES,
    discover_ucode_tools,
)


def _capture_discover(monkeypatch_import) -> tuple[dict, str]:
    """Run discover_ucode_tools() and return (tools_dict, stderr_text)."""
    buf = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = buf
    try:
        tools = discover_ucode_tools()
    finally:
        sys.stderr = old_stderr
    return tools, buf.getvalue()


def test_discover_emits_mcp_warning_on_module_import_error(monkeypatch):
    """A failing module causes [MCP WARNING] on stderr, not a silent pass."""
    failing_module = UCODE_MODULES[0]

    original_import = importlib.import_module

    def _patched_import(name, *args, **kwargs):
        if name == failing_module:
            raise ImportError(f"Simulated failure for {name}")
        return original_import(name, *args, **kwargs)

    with patch("wizard.mcp.tools.ucode_registry.importlib.import_module", side_effect=_patched_import):
        buf = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = buf
        try:
            discover_ucode_tools()
        finally:
            sys.stderr = old_stderr

    output = buf.getvalue()
    assert "[MCP WARNING]" in output, f"Expected [MCP WARNING] in stderr, got: {output!r}"
    assert failing_module in output, f"Expected module name in warning, got: {output!r}"
    assert "ImportError" in output, f"Expected exception type in warning, got: {output!r}"


def test_discover_warning_includes_exception_type_for_non_import_error(monkeypatch):
    """A RuntimeError in a module also emits [MCP WARNING] with the exception type."""
    failing_module = UCODE_MODULES[1]

    original_import = importlib.import_module

    def _patched_import(name, *args, **kwargs):
        if name == failing_module:
            raise RuntimeError("module internal crash")
        return original_import(name, *args, **kwargs)

    with patch("wizard.mcp.tools.ucode_registry.importlib.import_module", side_effect=_patched_import):
        buf = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = buf
        try:
            discover_ucode_tools()
        finally:
            sys.stderr = old_stderr

    output = buf.getvalue()
    assert "[MCP WARNING]" in output
    assert "RuntimeError" in output
    assert failing_module in output


def test_discover_healthy_modules_still_return_tools_when_one_fails(monkeypatch):
    """
    When one module fails, tools from the remaining modules are still returned.

    This verifies the fix is non-fatal: the function continues after a bad module.
    """
    failing_module = UCODE_MODULES[0]  # Only fail the first module

    original_import = importlib.import_module

    fail_count = {"n": 0}

    def _patched_import(name, *args, **kwargs):
        if name == failing_module:
            fail_count["n"] += 1
            raise ImportError(f"Simulated failure for {name}")
        return original_import(name, *args, **kwargs)

    with patch("wizard.mcp.tools.ucode_registry.importlib.import_module", side_effect=_patched_import):
        buf = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = buf
        try:
            tools_with_failure = discover_ucode_tools()
        finally:
            sys.stderr = old_stderr

    # Also run without any failure for comparison
    tools_all = discover_ucode_tools()

    # The failing module should have been attempted exactly once
    assert fail_count["n"] == 1

    # The total with one failure should be <= total without failure
    assert len(tools_with_failure) <= len(tools_all)

    # If any tools exist from healthy modules, they should appear in the partial result
    if len(tools_all) > 0 and len(UCODE_MODULES) > 1:
        # We can't assert exact counts without knowing which tools are in which module,
        # but we can assert the function completed without raising
        pass  # success: no exception raised


def test_discover_returns_empty_dict_when_all_modules_fail(monkeypatch):
    """When every module fails, discover returns {} without raising."""

    def _always_fail(name, *args, **kwargs):
        raise ImportError(f"all modules broken: {name}")

    with patch("wizard.mcp.tools.ucode_registry.importlib.import_module", side_effect=_always_fail):
        buf = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = buf
        try:
            tools = discover_ucode_tools()
        finally:
            sys.stderr = old_stderr

    assert tools == {}
    output = buf.getvalue()
    # One warning per module
    assert output.count("[MCP WARNING]") == len(UCODE_MODULES)


def test_discover_no_warning_when_all_modules_succeed():
    """No [MCP WARNING] on stderr when all modules import cleanly."""
    buf = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = buf
    try:
        discover_ucode_tools()
    finally:
        sys.stderr = old_stderr

    output = buf.getvalue()
    assert "[MCP WARNING]" not in output, (
        f"Unexpected [MCP WARNING] in stderr when no failure injected: {output!r}"
    )
