from core.services.gameplay_service import GameplayService
from core.tui.dispatcher import CommandDispatcher
from core.commands.gameplay_handler import GameplayHandler


def test_gameplay_service_stats_and_gate(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    stats = svc.get_user_stats("alice")
    assert stats == {"xp": 0, "hp": 100, "gold": 0}

    stats = svc.add_user_stat("alice", "xp", 25)
    assert stats["xp"] == 25

    assert svc.can_proceed() is False
    gate = svc.complete_gate("dungeon_l32_amulet", source="test")
    assert gate["completed"] is True
    assert svc.can_proceed() is True


def test_gameplay_tick_auto_gate_from_events(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    events_file.write_text(
        "\n".join(
            [
                '{"ts":"2026-02-15T00:00:00Z","source":"toybox:hethack","type":"HETHACK_LEVEL_REACHED","payload":{"depth":32}}',
                '{"ts":"2026-02-15T00:00:01Z","source":"toybox:hethack","type":"HETHACK_AMULET_RETRIEVED","payload":{"line":"You pick up the Amulet of Yendor"}}',
            ]
        )
        + "\n"
    )

    tick = svc.tick("alice")
    assert tick["processed"] == 2
    assert svc.can_proceed() is True
    stats = svc.get_user_stats("alice")
    assert stats["xp"] >= 510
    assert stats["gold"] >= 1000
    progress = svc.get_user_progress("alice")
    assert progress["achievement_level"] >= 1
    tokens = {row.get("id") for row in svc.get_user_unlock_tokens("alice")}
    assert "token.toybox.xp_100" in tokens
    assert "token.toybox.achievement_l1" in tokens
    assert "token.toybox.ascension" in tokens


def test_play_option_conditions_and_start(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    blocked = svc.start_play_option("alice", "galaxy")
    assert blocked["status"] == "blocked"
    assert "xp>=100" in blocked["blocked_by"]

    svc.add_user_stat("alice", "xp", 120)
    started = svc.start_play_option("alice", "galaxy")
    assert started["status"] == "success"


def test_rule_if_then_evaluates_against_play_state(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    svc.add_user_stat("alice", "xp", 120)
    svc.set_rule(
        "rule.test.unlock",
        if_expr="xp>=100 and achievement_level>=0",
        then_expr="TOKEN token.rule.test; PLAY galaxy",
        source="test",
    )
    result = svc.run_rules("alice", "rule.test.unlock")
    fired = result.get("fired", [])
    assert len(fired) == 1
    token_ids = {row.get("id") for row in svc.get_user_unlock_tokens("alice")}
    assert "token.rule.test" in token_ids


def test_gameplay_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY STATUS")
    assert result["status"] == "success"
    assert "PLAY STATUS" in result.get("output", "")


def test_play_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY OPTIONS")
    assert result["status"] == "success"
    assert "PLAY OPTIONS" in result.get("output", "")


def test_rule_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("RULE LIST")
    assert result["status"] == "success"
    assert "RULE LIST" in result.get("output", "")


def test_play_map_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY MAP STATUS")
    assert result["status"] == "success"
    assert "PLAY MAP STATUS" in result.get("output", "")


def test_play_lens_command_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY LENS STATUS")
    assert result["status"] == "success"
    assert "PLAY LENS STATUS" in result.get("output", "")


def test_play_lens_status_compact_is_dispatched():
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch("PLAY LENS STATUS --compact")
    assert result["status"] == "success"
    output = result.get("output", "")
    assert output.startswith("LENS:")
    assert " | " in output


def test_play_lens_status_includes_readiness_and_recommendation():
    handler = GameplayHandler()
    lens_status = {
        "version": "1",
        "lens": {"ready": False, "enabled": True, "enabled_source": "test", "blocking_reason": "gate"},
        "single_region": {"id": "region-1", "entry_place_id": "P1", "active": True},
        "slice_contract": {"valid": True, "allowed_place_ids": ["P1"]},
    }
    progression = {
        "active_lens": "elite",
        "stats": {"xp": 50, "gold": 3},
        "progress": {"level": 1, "achievement_level": 0},
        "blocked_requirements": ["xp>=100"],
        "play_options": [
            {"id": "dungeon", "available": True, "blocked_by": []},
            {"id": "galaxy", "available": False, "blocked_by": ["xp>=100"]},
            {"id": "social", "available": False, "blocked_by": ["achievement_level>=1"]},
            {"id": "ascension", "available": False, "blocked_by": ["gate:dungeon_l32_amulet"]},
        ],
        "unlock_tokens": [],
    }
    output = handler._format_lens_status(lens_status, progression, compact=False)
    assert "Readiness:" in output
    assert "Recommendation:" in output


def test_lens_score_and_checkpoints_views(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    svc.add_user_stat("alice", "xp", 125)
    svc.add_user_stat("alice", "gold", 40)

    checkpoints = svc.list_lens_checkpoints("alice", "elite")
    assert checkpoints["lens"] == "elite"
    assert checkpoints["summary"]["total"] >= 1

    score = svc.lens_score_view("alice", "elite")
    assert score["lens"] == "elite"
    assert score["score"]["total"] >= 125
    assert "tier" in score["score"]


def test_profile_overlay_resolution_and_commands(tmp_path):
    state_file = tmp_path / "gameplay_state.json"
    events_file = tmp_path / "events.ndjson"
    cursor_file = tmp_path / "cursor.json"
    svc = GameplayService(state_file=state_file, events_file=events_file, cursor_file=cursor_file)

    svc.set_profile_overlay("group", "alpha", "xp", 333)
    svc.set_profile_overlay("session", "run-1", "achievement_level", 2)
    svc.set_profile_overlay("session", "run-1", "metric.elite_jumps", 9)

    profile = svc.resolve_profile_variables("alice", group_id="alpha", session_id="run-1")
    effective = profile["effective"]["variables"]
    assert effective["xp"] == 333
    assert effective["achievement_level"] == 2
    assert profile["effective"]["metrics"]["elite_jumps"] == 9

    dispatcher = CommandDispatcher()
    status_result = dispatcher.dispatch("PLAY PROFILE STATUS --group alpha --session run-1")
    assert status_result["status"] == "success"
    assert "PLAY PROFILE STATUS" in status_result.get("output", "")

    score_result = dispatcher.dispatch("PLAY LENS SCORE elite --compact")
    assert score_result["status"] == "success"
    assert score_result.get("output", "").startswith("LENS:SCORE:elite")

    checkpoints_result = dispatcher.dispatch("PLAY LENS CHECKPOINTS elite --compact")
    assert checkpoints_result["status"] == "success"
    assert checkpoints_result.get("output", "").startswith("LENS:CHECKPOINTS:elite")
