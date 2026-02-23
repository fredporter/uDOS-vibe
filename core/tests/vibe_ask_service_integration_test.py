"""Integration-style tests for VibeAskService backend failure/recovery paths."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from core.services.vibe_ask_service import AskBackend, VibeAskService


def test_query_without_backend_reports_unavailable() -> None:
    with patch("core.services.vibe_ask_service.shutil.which", return_value=None):
        service = VibeAskService()

    result = service.query("hello")
    assert result["status"] == "error"
    assert "unavailable" in result["message"].lower()
    assert result["backend"] == AskBackend.NONE.value


def test_query_failure_then_recovery_same_instance() -> None:
    with patch("core.services.vibe_ask_service.shutil.which", return_value="/usr/bin/ollama"):
        service = VibeAskService()

    timeout = subprocess.TimeoutExpired(cmd=["ollama", "run"], timeout=120)
    success = subprocess.CompletedProcess(
        args=["ollama", "run", "mistral", "hello"],
        returncode=0,
        stdout="Recovered response",
        stderr="",
    )

    with patch(
        "core.services.vibe_ask_service.subprocess.run",
        side_effect=[timeout, success],
    ):
        first = service.query("hello")
        second = service.query("hello")

    assert first["status"] == "error"
    assert "timeout" in first["message"].lower()
    assert second["status"] == "success"
    assert second["response"] == "Recovered response"
    assert second["backend"] == AskBackend.OLLAMA.value


def test_explain_and_suggest_use_backend_response() -> None:
    with patch("core.services.vibe_ask_service.shutil.which", return_value="/usr/bin/ollama"):
        service = VibeAskService()

    explain_ok = subprocess.CompletedProcess(
        args=["ollama", "run", "mistral", "explain"],
        returncode=0,
        stdout="Topic explanation",
        stderr="",
    )
    suggest_ok = subprocess.CompletedProcess(
        args=["ollama", "run", "mistral", "suggest"],
        returncode=0,
        stdout="- one\n- two\n- three\n- four",
        stderr="",
    )

    with patch(
        "core.services.vibe_ask_service.subprocess.run",
        side_effect=[explain_ok, suggest_ok],
    ):
        explained = service.explain("dispatch", "brief")
        suggested = service.suggest("stabilize routing")

    assert explained["status"] == "success"
    assert explained["explanation"] == "Topic explanation"
    assert suggested["status"] == "success"
    assert suggested["suggestions"] == ["one", "two", "three"]
