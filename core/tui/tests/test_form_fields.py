from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from core.commands.setup_handler import SetupHandler
from core.tui.form_fields import DateTimeApproval
from core.tui.form_fields import FieldType
from core.tui.form_fields import TUIFormRenderer
from core.tui.story_form_handler import StoryFormHandler

FIXED_NOW = datetime(2026, 1, 31, 20, 45, 12, tzinfo=timezone.utc)


def _patched_now(*args, **kwargs):
    return FIXED_NOW


@pytest.mark.parametrize(
    "input_key,expected_timezone,expected_approval",
    [
        ("\n", "UTC", True),
        ("y", "UTC", True),
        ("n", "America/Los_Angeles", False),
    ],
)
def test_datetime_approval_handles_inputs(input_key, expected_timezone, expected_approval):
    with patch.object(DateTimeApproval, "_get_now", side_effect=_patched_now):
        approval = DateTimeApproval("Confirm date/time", timezone_hint=expected_timezone)
        result = approval.handle_input(input_key)

    assert result is not None, "Input should return approval payload"
    assert result["approved"] is expected_approval
    assert result["date"] == "2026-01-31"
    assert result["time"] == "20:45:12"
    assert result["timezone"] == expected_timezone


def test_datetime_approval_render_contains_clock():
    with patch.object(DateTimeApproval, "_get_now", side_effect=_patched_now):
        approval = DateTimeApproval("Confirm date/time", timezone_hint="UTC")
        rendered = approval.render(focused=True)

    assert "2026-01-31" in rendered
    assert "Timezone:" in rendered


def _approval_payload(approved: bool = True) -> dict:
    return {
        "approved": approved,
        "date": "2026-01-31",
        "time": "20:45:12",
        "timezone": "UTC",
    }


def test_apply_system_datetime_runs_override_form_on_decline():
    handler = SetupHandler()
    overrides = {
        "user_timezone": "Europe/London",
        "current_date": "2026-01-31",
        "current_time": "09:00:00",
    }
    approval = _approval_payload(approved=False)

    with patch.object(SetupHandler, "_run_datetime_override_form", return_value={"status": "success", "data": overrides}) as override_mock:
        updated = handler._apply_system_datetime({"system_datetime_approve": approval.copy()})

    assert override_mock.called, "Declining approval should trigger override form"
    assert updated["user_timezone"] == overrides["user_timezone"]
    assert updated["current_date"] == overrides["current_date"]
    assert updated["current_time"] == overrides["current_time"]


def test_apply_system_datetime_falls_back_to_system_timezone():
    handler = SetupHandler()
    approval = _approval_payload(approved=False)

    with patch.object(SetupHandler, "_run_datetime_override_form", return_value={"status": "error", "message": "fallback"}):
        with patch.object(SetupHandler, "_get_system_timezone", return_value="UTC"):
            updated = handler._apply_system_datetime({"system_datetime_approve": approval.copy()})

    assert updated["user_timezone"] == "UTC"


def test_apply_system_datetime_prefers_manual_override_data():
    handler = SetupHandler()
    approval = _approval_payload(approved=False)
    form_data = {
        "system_datetime_approve": approval.copy(),
        "user_timezone": "Europe/London",
        "current_date": "2026-01-31",
        "current_time": "09:00:00",
    }

    with patch.object(SetupHandler, "_run_datetime_override_form") as override_mock:
        updated = handler._apply_system_datetime(form_data)

    assert override_mock.call_count == 0
    assert updated["user_timezone"] == "Europe/London"
    assert updated["current_date"] == "2026-01-31"
    assert updated["current_time"] == "09:00:00"


def test_story_handler_reorders_location_fields_last():
    handler = StoryFormHandler()
    renderer = TUIFormRenderer(title="test")
    handler.renderer = renderer
    renderer.fields = [
        {"name": "user_timezone", "type": FieldType.LOCATION, "widget": None, "value": None},
        {"name": "user_role", "type": FieldType.TEXT, "widget": None, "value": "admin"},
    ]
    handler._reorder_location_fields()

    assert renderer.fields[-1]["type"] == FieldType.LOCATION


def test_story_handler_inserts_override_fields_after_decline():
    handler = StoryFormHandler()
    renderer = TUIFormRenderer(title="override")
    handler.renderer = renderer
    handler.renderer.fields = [
        {"name": "system_datetime_approve", "type": FieldType.DATETIME_APPROVE, "widget": None, "value": None},
        {"name": "user_location", "type": FieldType.LOCATION, "widget": None, "value": None},
    ]
    handler.renderer.current_field_index = 0

    approvals = {"timezone": "UTC", "date": "2026-01-31", "time": "09:00:00"}
    handler._insert_datetime_override_fields(approvals)

    names = [field["name"] for field in renderer.fields]
    assert names[1:4] == ["user_timezone", "current_date", "current_time"]
    assert renderer.fields[-1]["type"] == FieldType.LOCATION
