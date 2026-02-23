from __future__ import annotations

from core.services.compact_status_service import format_compact_status


def test_format_compact_status_respects_order():
    output = format_compact_status(
        "MODE:dev",
        {"gold": 10, "xp": 25, "fit": "aligned"},
        order=["xp", "gold", "fit"],
    )
    assert output == "MODE:dev | xp=25 | gold=10 | fit=aligned"


def test_format_compact_status_sanitizes_pipes():
    output = format_compact_status(
        "SKIN",
        {"policy": "skin|lens", "skin": "dungeon"},
        order=["skin", "policy"],
    )
    assert output == "SKIN: | skin=dungeon | policy=skin/lens"
