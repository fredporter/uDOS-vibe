from __future__ import annotations

from core.services.progression_contract_service import (
    build_progression_contract,
    build_skin_policy_context,
)


def test_progression_contract_maps_variables_tokens_and_lens_readiness() -> None:
    snapshot = {
        "active_lens": "elite",
        "stats": {"xp": 40, "hp": 80, "gold": 10},
        "progress": {"level": 2, "achievement_level": 0, "metrics": {"elite_jumps": 1}},
        "unlock_tokens": [{"id": "token.toybox.navigator_l1"}],
        "play_options": [
            {"id": "dungeon", "available": True, "blocked_by": []},
            {"id": "galaxy", "available": False, "blocked_by": ["xp>=100"]},
            {"id": "social", "available": False, "blocked_by": ["achievement_level>=1"]},
            {"id": "ascension", "available": False, "blocked_by": ["gate:dungeon_l32_amulet"]},
        ],
        "blocked_requirements": ["xp>=100", "achievement_level>=1"],
    }
    contract = build_progression_contract(snapshot)
    assert contract["variables"]["xp"] == 40
    assert contract["variables"]["hp"] == 80
    assert contract["variables"]["gold"] == 10
    assert contract["variables"]["level"] == 2
    assert contract["variables"]["achievement_level"] == 0
    assert "token.toybox.navigator_l1" in contract["unlock_token_ids"]
    readiness = contract["lens_readiness"]["elite"]
    assert readiness["available"] is False
    assert readiness["option_id"] == "galaxy"
    assert "xp>=100" in readiness["blocked_by"]
    assert "Increase XP" in (readiness["recommendation"] or "")


def test_skin_policy_context_flags_progression_drift_non_blocking() -> None:
    progression = {
        "active_lens": "elite",
        "stats": {"xp": 50, "hp": 100, "gold": 5},
        "progress": {"level": 1, "achievement_level": 0},
        "unlock_tokens": [],
        "play_options": [
            {"id": "dungeon", "available": True, "blocked_by": []},
            {"id": "galaxy", "available": False, "blocked_by": ["xp>=100"]},
            {"id": "social", "available": False, "blocked_by": ["achievement_level>=1"]},
            {"id": "ascension", "available": False, "blocked_by": ["gate:dungeon_l32_amulet"]},
        ],
        "blocked_requirements": ["xp>=100"],
    }
    policy = build_skin_policy_context(
        progression=progression,
        selected_skin="galaxy",
        available_skins=["default", "galaxy", "dungeon"],
    )
    assert policy.policy_flag == "skin_lens_progression_drift"
    assert "not enforce" in (policy.policy_note or "").lower()

