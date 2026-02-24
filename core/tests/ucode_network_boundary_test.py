"""Boundary policy tests for uCODE networking helpers."""

from __future__ import annotations

from core.tui.ucode import UCODE


class _LoggerStub:
    def warning(self, *_args, **_kwargs) -> None:
        return None


def _ucode_stub() -> UCODE:
    ucode = UCODE.__new__(UCODE)
    ucode.logger = _LoggerStub()
    ucode._env_file_cache = {}
    return ucode


def test_resolve_loopback_url_accepts_localhost() -> None:
    ucode = _ucode_stub()
    resolved = ucode._resolve_loopback_url(
        "http://localhost:8765",
        fallback="http://127.0.0.1:8765",
        context="WIZARD_BASE_URL",
    )
    assert resolved == "http://localhost:8765"


def test_resolve_loopback_url_blocks_non_loopback() -> None:
    ucode = _ucode_stub()
    resolved = ucode._resolve_loopback_url(
        "https://wizard.example.com",
        fallback="http://127.0.0.1:8765",
        context="WIZARD_BASE_URL",
    )
    assert resolved == "http://127.0.0.1:8765"


def test_wizard_base_url_falls_back_to_loopback(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_env_value", lambda key: "https://wizard.example.com")
    assert ucode._wizard_base_url() == "http://127.0.0.1:8765"


def test_get_ok_local_status_sanitizes_ollama_endpoint(monkeypatch) -> None:
    """Test that non-loopback endpoints are sanitized to localhost."""
    from unittest.mock import Mock
    from core.services.ai_provider_handler import ProviderStatus
    
    ucode = _ucode_stub()
    
    # Mock AIProviderHandler to return a status with non-loopback endpoint
    mock_status = ProviderStatus(
        provider_id="ollama",
        is_configured=True,
        is_running=True,
        is_available=True,
        loaded_models=["model-a"],
        default_model="model-a",
        issue=None,
        details={"endpoint": "http://ollama"},  # Non-loopback hostname
    )
    
    mock_handler = Mock()
    mock_handler.check_local_provider.return_value = mock_status
    
    from core.services import ai_provider_handler
    monkeypatch.setattr(
        ai_provider_handler,
        "get_ai_provider_handler",
        lambda: mock_handler
    )
    
    status = ucode._get_ok_local_status()
    assert status["ready"] is True
    # Non-loopback endpoint should be sanitized to localhost
    assert status["ollama_endpoint"] == "http://127.0.0.1:11434"
