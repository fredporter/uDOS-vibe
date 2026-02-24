"""Tests for Ollama Tier Service."""

from __future__ import annotations

import pytest

from wizard.services.ollama_tier_service import (
    DEFAULT_TIER,
    TIER1_MODELS,
    TIER2_MODELS,
    TIER3_MODELS,
    detect_missing_models,
    get_required_models,
    get_tier_profile,
    normalize_model_name,
)


class TestTierBaselines:
    def test_tier1_is_minimal(self):
        """tier1 should have fewest models."""
        assert len(TIER1_MODELS) < len(TIER2_MODELS)

    def test_tier2_is_midrange(self):
        """tier2 should have fewer models than tier3."""
        assert len(TIER2_MODELS) < len(TIER3_MODELS)

    def test_all_tiers_include_mistral(self):
        """All tiers should require mistral as the primary model."""
        for models in (TIER1_MODELS, TIER2_MODELS, TIER3_MODELS):
            assert "mistral" in models

    def test_mistral_is_first_in_all_tiers(self):
        """Mistral should be first in each tier list."""
        for models in (TIER1_MODELS, TIER2_MODELS, TIER3_MODELS):
            assert models[0] == "mistral"


class TestGetTierProfile:
    def test_tier1_profile(self):
        profile = get_tier_profile("tier1")
        assert profile.tier == "tier1"
        assert profile.models == TIER1_MODELS
        assert profile.default_model == "mistral"

    def test_tier2_profile(self):
        profile = get_tier_profile("tier2")
        assert profile.tier == "tier2"
        assert profile.models == TIER2_MODELS

    def test_tier3_profile(self):
        profile = get_tier_profile("tier3")
        assert profile.tier == "tier3"
        assert profile.models == TIER3_MODELS

    def test_unknown_tier_falls_back_to_default(self):
        profile = get_tier_profile("tier99")
        assert profile.tier == DEFAULT_TIER

    def test_none_tier_falls_back_to_default(self):
        profile = get_tier_profile(None)
        assert profile.tier == DEFAULT_TIER

    def test_empty_tier_falls_back_to_default(self):
        profile = get_tier_profile("")
        assert profile.tier == DEFAULT_TIER


class TestGetRequiredModels:
    def test_returns_tier1_models_for_tier1(self):
        models = get_required_models(tier="tier1")
        assert models == TIER1_MODELS

    def test_returns_tier3_models_for_tier3(self):
        models = get_required_models(tier="tier3")
        assert models == TIER3_MODELS

    def test_override_takes_precedence(self):
        models = get_required_models(tier="tier3", override="phi3,gemma2")
        assert models == ["phi3", "gemma2"]

    def test_override_strips_whitespace(self):
        models = get_required_models(tier="tier1", override=" mistral , llama3.2 ")
        assert models == ["mistral", "llama3.2"]

    def test_empty_override_uses_tier(self):
        models = get_required_models(tier="tier1", override="")
        assert models == TIER1_MODELS


class TestNormalizeModelName:
    def test_strips_tag(self):
        assert normalize_model_name("mistral:latest") == "mistral"

    def test_no_tag_unchanged(self):
        assert normalize_model_name("mistral") == "mistral"

    def test_strips_specific_tag(self):
        assert normalize_model_name("llama3.2:8b-instruct-q4_K_M") == "llama3.2"


class TestDetectMissingModels:
    def test_all_present_returns_empty(self):
        required = ["mistral", "llama3.2"]
        running = ["mistral:latest", "llama3.2:latest"]
        assert detect_missing_models(required, running) == []

    def test_detects_missing_model(self):
        required = ["mistral", "llama3.2", "qwen3"]
        running = ["mistral:latest"]
        missing = detect_missing_models(required, running)
        assert "llama3.2" in missing
        assert "qwen3" in missing
        assert "mistral" not in missing

    def test_tag_agnostic_comparison(self):
        required = ["mistral"]
        running = ["mistral:7b-instruct-v0.3-q6_K"]
        assert detect_missing_models(required, running) == []

    def test_empty_running_returns_all_required(self):
        required = ["mistral", "llama3.2"]
        assert detect_missing_models(required, []) == required
