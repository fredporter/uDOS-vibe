from unittest.mock import patch

from core.tui.story_form_handler import (
    SimpleFallbackFormHandler,
    StoryFormHandler,
    StoryFormSession,
    get_form_handler,
)


def test_get_form_handler_returns_fallback_without_tty():
    with patch("core.tui.story_form_handler._interactive_tty_available", return_value=False):
        handler = get_form_handler()

    assert isinstance(handler, SimpleFallbackFormHandler)


def test_get_form_handler_falls_back_when_story_handler_errors():
    with patch("core.tui.story_form_handler._interactive_tty_available", return_value=True):
        with patch("core.tui.story_form_handler.StoryFormHandler", side_effect=RuntimeError("boom")):
            handler = get_form_handler()

    assert isinstance(handler, SimpleFallbackFormHandler)


def test_story_form_session_roundtrip():
    form_spec = {
        "title": "Setup",
        "fields": [
            {"name": "user_name", "label": "Name", "type": "text", "required": True},
            {"name": "system_datetime_approve", "label": "Approve time", "type": "datetime_approve"},
        ],
    }

    session = StoryFormSession(form_spec)
    prompt1 = session.get_prompt()
    assert prompt1 and "vibe_input" in prompt1
    assert prompt1["vibe_input"]["id"] == "user_name"

    result1 = session.submit_response("user_name", "Ada")
    assert result1["status"] == "ok"

    prompt2 = session.get_prompt()
    assert prompt2["vibe_input"]["id"] == "system_datetime_approve"

    result2 = session.submit_response("system_datetime_approve", {"approved": True, "timezone": "UTC"})
    assert result2["status"] == "ok"

    assert session.is_complete()
