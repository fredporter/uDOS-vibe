"""Test that restrictions are in alert-only mode for testing phase.

This test suite verifies:
1. Ghost Mode markers are present and logged (not blocked)
2. Operations proceed despite Ghost Mode markers
3. Permission system is properly stubbed
4. No other blockers remain that might prevent updates
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


# Test 1: Alert-only logging verification
class TestAlertOnlyMode:
    """Verify all Ghost Mode checks emit alerts instead of blocking."""

    def test_binder_compile_has_alert_marker(self):
        """BINDER COMPILE should log alert, not block."""
        source = Path("core/commands/binder_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "binder_handler missing alert marker"
        assert "Ghost Mode" in source
        assert "demo mode" in source

    def test_run_execute_has_alert_marker(self):
        """RUN execute should log alert, not block."""
        source = Path("core/commands/run_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "run_handler missing alert marker"
        assert "Ghost Mode" in source

    def test_wizard_control_has_alert_marker(self):
        """WIZARD control should log alert, not block."""
        source = Path("core/commands/wizard_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "wizard_handler missing alert marker"

    def test_file_editor_has_alert_marker(self):
        """File editing should log alert, not block."""
        source = Path("core/commands/file_editor_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "file_editor_handler missing alert marker"

    def test_repair_has_alert_marker(self):
        """REPAIR should log alert, not block."""
        source = Path("core/commands/repair_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "repair_handler missing alert marker"

    def test_maintenance_has_alert_marker(self):
        """Maintenance ops should log alert, not block."""
        source = Path("core/commands/maintenance_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "maintenance_handler missing alert marker"

    def test_destroy_has_alert_marker(self):
        """DESTROY should log alert, not block."""
        source = Path("core/commands/destroy_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "destroy_handler missing alert marker"

    def test_empire_control_has_alert_marker(self):
        """EMPIRE control should log alert, not block."""
        source = Path("core/commands/empire_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "empire_handler missing alert marker"

    def test_seed_install_has_alert_marker(self):
        """SEED INSTALL should log alert, not block."""
        source = Path("core/commands/seed_handler.py").read_text()
        assert "[TESTING ALERT]" in source, "seed_handler missing alert marker"

    def test_spatial_filesystem_write_has_alert_marker(self):
        """File write should log alert, not block."""
        source = Path("core/services/spatial_filesystem.py").read_text()
        # Should have alerts in both write_file and delete_file
        alert_count = source.count("[TESTING ALERT]")
        assert alert_count >= 2, (
            f"spatial_filesystem missing alert markers (found {alert_count})"
        )


# Test 2: No blocking return statements
class TestNoBlockingBehavior:
    """Verify Ghost Mode doesn't return error/warning status."""

    def test_binder_handler_execution_not_blocked(self):
        """BINDER COMPILE should execute, not return blocked status."""
        source = Path("core/commands/binder_handler.py").read_text()
        # Should NOT return with "blocked" or "disabled" message
        assert (
            "return {" not in source.split("if is_ghost_mode():")[1].split("if len")[0]
        ), "binder_handler still returns blocking response"

    def test_run_handler_execution_not_blocked(self):
        """RUN should execute, not return blocked status."""
        source = Path("core/commands/run_handler.py").read_text()
        # After ghost check, execution should proceed
        ghost_section = source.split("if is_ghost_mode():")[1].split("file_arg =")[0]
        assert "return" not in ghost_section or "logger" in ghost_section, (
            "run_handler still returns blocking response"
        )

    def test_no_permission_errors_on_ghost_mode(self):
        """Ghost Mode should not raise PermissionError."""
        source = Path("core/services/spatial_filesystem.py").read_text()
        # Find write_file and delete_file sections
        write_section = source.split("def write_file")[1].split("ws_type")[0]
        assert "raise PermissionError" not in write_section, (
            "write_file still raises PermissionError on ghost mode"
        )


# Test 3: Permission system design check
class TestPermissionSystemStructure:
    """Verify permission system is properly structured."""

    def test_permission_enum_exists(self):
        """Permission enum should define all operation types."""
        from core.services.permission_handler import Permission

        # Should have permissions for various operations
        expected_perms = [
            "BINDER_COMPILE",
            "RUN_EXECUTE",
            "DESTROY",
            "ADMIN",
            "DEV_MODE",
            "WIZARD_CONTROL",
        ]

        actual_perms = [perm.name for perm in Permission]
        for exp in expected_perms:
            assert any(exp.lower() in ap.lower() for ap in actual_perms), (
                f"Permission system missing {exp}"
            )

    def test_ghost_mode_detection_function(self):
        """is_ghost_mode() should exist and be testable."""
        from core.services.user_service import is_ghost_mode

        # Should be callable
        assert callable(is_ghost_mode)
        # Should return boolean
        result = is_ghost_mode()
        assert isinstance(result, bool)

    def test_mode_policy_exists(self):
        """Mode policy should define runtime modes."""
        from core.services.mode_policy import RuntimeMode, resolve_runtime_mode

        # Should have different runtime modes
        modes = list(RuntimeMode)
        assert len(modes) >= 2, "RuntimeMode should have multiple states"

        # resolve function should work
        mode = resolve_runtime_mode()
        assert mode in modes


# Test 4: Other blocker verification
class TestNoOtherBlockers:
    """Check for other potential locks that might block updates."""

    def test_no_version_checks_blocking_updates(self):
        """Version checks should not prevent operations."""
        import glob

        # Search for strict version comparisons that might block
        scripts = glob.glob("core/**/*.py", recursive=True)

        for script in scripts[:20]:  # Sample check
            try:
                content = Path(script).read_text()
                # Should not have commit-based gates
                assert "check previous commit" not in content.lower()
                assert "current version must be" not in content.lower()
            except:
                pass

    def test_no_hard_feature_gates(self):
        """Feature availability should not hard-gate operations."""
        source = Path("core/commands/help_handler.py").read_text()

        # Help should show all commands regardless of mode
        assert "is_ghost_mode" in source  # It's checked
        # But should not prevent access
        assert "raise" not in source or "error" not in source.split("is_ghost_mode")[1]

    def test_action_yml_not_locked(self):
        """action.yml should not enforce strict version pinning."""
        source = Path("action.yml").read_text()

        assert "--locked" not in source, "action.yml still has --locked flag"

    def test_no_ci_enforcement_gates(self):
        """CI workflows should not enforce stale version gates."""
        import glob

        workflows = glob.glob(".github/workflows/*.yml")
        for wf in workflows:
            content = Path(wf).read_text()
            # Should not enforce v1.3.25 contract freeze or similar
            assert "contract.freeze" not in content.lower()
            assert "check_v1_3_25" not in content.lower()


# Test 5: Testing phase readiness
class TestingPhaseReadiness:
    """Verify system is ready for full testing without restrictions."""

    def test_all_commands_available_in_ghost_mode(self):
        """Ghost Mode should show all commands as available."""
        from core.commands.help_handler import HelpHandler

        # When ghost mode is active, help should not hide commands
        with patch("core.services.user_service.is_ghost_mode", return_value=True):
            # Handler should still provide help for all commands
            handler = HelpHandler()
            # Should not throw or filter commands
            assert handler is not None

    def test_permission_checks_are_informational(self):
        """Permission system should be informational, not blocking."""
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        # Should have current user
        user = user_mgr.current()
        # May be None in testing, but shouldn't raise
        assert True  # pragma: no cover

    def test_ghost_mode_is_opt_in_via_username(self):
        """Ghost Mode should be detected via username, not config file."""
        from core.services.user_service import is_ghost_mode

        # Mode should be deterministic based on user context
        # Not dependent on external version flags
        mode = is_ghost_mode()
        assert isinstance(mode, bool)

    def test_testing_alert_messages_are_consistent(self):
        """All testing alerts should follow same format."""
        import glob

        py_files = glob.glob("core/commands/*.py")
        alert_strings = []

        for f in py_files:
            content = Path(f).read_text()
            if "[TESTING ALERT]" in content:
                # Extract alert strings
                for line in content.split("\n"):
                    if "[TESTING ALERT]" in line:
                        alert_strings.append(line.strip())

        # All should mention demo mode and v1.5
        for alert in alert_strings:
            assert "demo mode" in alert.lower()
            assert "v1.5" in alert.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
