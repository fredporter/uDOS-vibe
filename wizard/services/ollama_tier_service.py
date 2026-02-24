"""Ollama Tier Service

Defines per-tier Ollama model baselines and provides helpers for
tier-aware model selection and validation.

Tiers reflect hardware capability:
  tier1 — minimal (e.g. Raspberry Pi 5, 8 GB RAM, 4 CPU cores)
  tier2 — mid-range (e.g. consumer laptop, 16 GB RAM)
  tier3 — high-end workstation (32+ GB RAM, dedicated GPU or Apple Silicon)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ============================================================
# Tier baselines
# ============================================================

#: Smallest footprint — one reliable general-purpose model.
TIER1_MODELS: list[str] = [
    "mistral",  # 4 GB RAM — primary model
]

#: Mid-range — adds coding and small reasoning model.
TIER2_MODELS: list[str] = [
    "mistral",          # 4 GB RAM — general-purpose
    "llama3.2",         # 2 GB RAM — fast small model
    "qwen3",            # 4 GB RAM — reasoning / coding
]

#: Full workstation suite — complete capability matrix.
TIER3_MODELS: list[str] = [
    "mistral",
    "devstral-small-2",
    "llama3.2",
    "qwen3",
    "codellama",
    "phi3",
    "gemma2",
    "deepseek-coder",
]

KNOWN_TIERS: dict[str, list[str]] = {
    "tier1": TIER1_MODELS,
    "tier2": TIER2_MODELS,
    "tier3": TIER3_MODELS,
}

DEFAULT_TIER = "tier2"


@dataclass
class TierProfile:
    tier: str
    models: list[str] = field(default_factory=list)
    default_model: str = "mistral"


def get_tier_profile(tier: str | None = None) -> TierProfile:
    """Return the TierProfile for the given tier identifier.

    Falls back to DEFAULT_TIER if the tier is unknown or None.
    """
    resolved = (tier or "").strip().lower()
    if resolved not in KNOWN_TIERS:
        resolved = DEFAULT_TIER
    models = list(KNOWN_TIERS[resolved])
    return TierProfile(tier=resolved, models=models, default_model=models[0] if models else "mistral")


def get_required_models(tier: str | None = None, override: str | None = None) -> list[str]:
    """Return the required model list for a tier.

    Args:
        tier: Tier identifier (tier1 / tier2 / tier3).
        override: Comma-separated model list that overrides tier defaults.

    Returns:
        Ordered list of required model names (base names, no tags).
    """
    if override and override.strip():
        return [m.strip() for m in override.split(",") if m.strip()]

    return list(get_tier_profile(tier).models)


def normalize_model_name(name: str) -> str:
    """Strip tag suffix from a model name (e.g. 'mistral:latest' → 'mistral')."""
    return name.split(":")[0]


def detect_missing_models(
    required: list[str],
    running: list[str],
) -> list[str]:
    """Return required models not present in the running list.

    Comparison is by normalized base name (ignores :tags).
    """
    running_bases = {normalize_model_name(m) for m in running}
    return [m for m in required if normalize_model_name(m) not in running_bases]
