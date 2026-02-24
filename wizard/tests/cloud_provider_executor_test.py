"""Tests for CloudProviderExecutor multi-provider fallback chain."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from wizard.services.cloud_provider_executor import (
    get_cloud_availability,
    run_cloud_with_fallback,
)


# ============================================================
# Availability checks
# ============================================================


class TestGetCloudAvailability:
    def test_ready_when_at_least_one_key_configured(self):
        with patch.dict("os.environ", {"MISTRAL_API_KEY": "sk-test"}, clear=False):
            result = get_cloud_availability()
        assert result["ready"] is True
        assert result["issue"] is None
        assert "mistral" in result["available_providers"]

    def test_not_ready_when_no_keys_configured(self):
        env_keys = [
            "MISTRAL_API_KEY", "OPENROUTER_API_KEY",
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
            "STAGING_MISTRAL_API_KEY", "GOOGLE_API_KEY",
        ]
        with patch("wizard.services.cloud_provider_executor._env_getter", return_value=""):
            result = get_cloud_availability()
        assert result["ready"] is False
        assert result["available_providers"] == []

    def test_primary_is_first_available_in_chain(self):
        def env_getter(key: str) -> str:
            # Only OpenAI is configured
            return "sk-openai" if key == "OPENAI_API_KEY" else ""

        with patch("wizard.services.cloud_provider_executor._env_getter", side_effect=env_getter):
            result = get_cloud_availability()

        assert result["ready"] is True
        assert "openai" in result["available_providers"]

    def test_multiple_providers_listed_when_multiple_keys(self):
        def env_getter(key: str) -> str:
            keys = {"MISTRAL_API_KEY": "sk-m", "OPENAI_API_KEY": "sk-o"}
            return keys.get(key, "")

        with patch("wizard.services.cloud_provider_executor._env_getter", side_effect=env_getter):
            result = get_cloud_availability()

        assert result["ready"] is True
        assert len(result["available_providers"]) >= 2


# ============================================================
# Fallback chain execution
# ============================================================


class TestRunCloudWithFallback:
    def _make_response(self, text: str, model: str = "mistral-small-latest"):
        """Helper to create a mock 200 response."""
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {
            "choices": [{"message": {"content": text}}]
        }
        return mock

    def test_raises_when_no_providers_configured(self):
        with patch("wizard.services.cloud_provider_executor._env_getter", return_value=""):
            with pytest.raises(RuntimeError, match="All cloud providers failed"):
                run_cloud_with_fallback("hello")

    def test_returns_response_and_model_on_success(self):
        def env_getter(key: str) -> str:
            return "sk-test" if key == "MISTRAL_API_KEY" else ""

        mock_resp = self._make_response("hello back")

        with patch("wizard.services.cloud_provider_executor._env_getter", side_effect=env_getter):
            with patch("wizard.services.cloud_provider_executor._load_context", return_value=""):
                with patch("requests.post", return_value=mock_resp):
                    response, model = run_cloud_with_fallback("hello")

        assert response == "hello back"
        assert isinstance(model, str) and model

    def test_falls_over_to_second_provider_on_auth_error(self):
        call_count = {"n": 0}

        def env_getter(key: str) -> str:
            both = {"MISTRAL_API_KEY": "sk-m", "OPENAI_API_KEY": "sk-o"}
            return both.get(key, "")

        def mock_post(*args, **kwargs):
            call_count["n"] += 1
            mock = MagicMock()
            if call_count["n"] == 1:
                # First call (Mistral) returns 401
                mock.status_code = 401
                mock.json.return_value = {}
            else:
                # Second call (OpenAI-style) returns 200
                mock.status_code = 200
                mock.json.return_value = {
                    "choices": [{"message": {"content": "openai response"}}]
                }
            return mock

        with patch("wizard.services.cloud_provider_executor._env_getter", side_effect=env_getter):
            with patch("wizard.services.cloud_provider_executor._load_context", return_value=""):
                with patch("requests.post", side_effect=mock_post):
                    response, model = run_cloud_with_fallback("test prompt")

        assert response == "openai response"
        assert call_count["n"] == 2

    def test_raises_after_all_providers_fail(self):
        def env_getter(key: str) -> str:
            return "sk-test" if key in {"MISTRAL_API_KEY", "OPENAI_API_KEY"} else ""

        def mock_post(*args, **kwargs):
            mock = MagicMock()
            mock.status_code = 429  # Rate limit — should failover
            mock.json.return_value = {}
            return mock

        with patch("wizard.services.cloud_provider_executor._env_getter", side_effect=env_getter):
            with patch("wizard.services.cloud_provider_executor._load_context", return_value=""):
                with patch("requests.post", side_effect=mock_post):
                    with pytest.raises(RuntimeError, match="All cloud providers failed"):
                        run_cloud_with_fallback("test prompt")


# ============================================================
# Context injection
# ============================================================


class TestContextInjection:
    def test_context_injected_as_system_message_for_openai_style(self):
        """Context should appear as a system message for OpenAI/Mistral."""
        from core.services.cloud_provider_policy import CloudProvider
        from wizard.services.cloud_provider_executor import _inject_context_into_request

        payload = {"messages": [{"role": "user", "content": "hello"}]}
        result = _inject_context_into_request(payload, "CONTEXT", CloudProvider.MISTRAL)

        messages = result["messages"]
        assert messages[0]["role"] == "system"
        assert "CONTEXT" in messages[0]["content"]

    def test_context_injected_as_system_field_for_anthropic(self):
        """Context should appear as top-level 'system' for Anthropic."""
        from core.services.cloud_provider_policy import CloudProvider
        from wizard.services.cloud_provider_executor import _inject_context_into_request

        payload = {
            "messages": [{"role": "user", "content": "hello"}],
            "model": "claude-3-5-sonnet-latest",
        }
        result = _inject_context_into_request(payload, "CONTEXT", CloudProvider.ANTHROPIC)

        assert "system" in result
        assert "CONTEXT" in result["system"]

    def test_context_prepended_for_gemini(self):
        """Context should be prepended to first user part for Gemini."""
        from core.services.cloud_provider_policy import CloudProvider
        from wizard.services.cloud_provider_executor import _inject_context_into_request

        payload = {
            "contents": [{"parts": [{"text": "user prompt"}]}]
        }
        result = _inject_context_into_request(payload, "CONTEXT", CloudProvider.GEMINI)

        first_text = result["contents"][0]["parts"][0]["text"]
        assert "CONTEXT" in first_text
        assert "user prompt" in first_text

    def test_empty_context_returns_unchanged_payload(self):
        """Empty context should not modify payload."""
        from core.services.cloud_provider_policy import CloudProvider
        from wizard.services.cloud_provider_executor import _inject_context_into_request

        payload = {"messages": [{"role": "user", "content": "hello"}]}
        result = _inject_context_into_request(payload, "  ", CloudProvider.MISTRAL)

        assert result == payload
