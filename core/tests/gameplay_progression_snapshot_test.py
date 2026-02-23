from __future__ import annotations

from core.services.gameplay_service import GameplayService


def test_progression_snapshot_has_canonical_fields(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    service = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    service.add_user_stat("alice", "xp", 120)
    service.add_user_stat("alice", "gold", 50)
    snapshot = service.progression_snapshot("alice")

    assert snapshot["active_lens"] in {"hethack", "elite", "rpgbbs", "crawler3d"}
    assert "stats" in snapshot
    assert "progress" in snapshot
    assert "unlock_tokens" in snapshot
    assert "play_options" in snapshot
    assert "blocked_requirements" in snapshot
    assert snapshot["stats"]["xp"] == 120
    assert snapshot["stats"]["gold"] == 50
