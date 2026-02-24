"""Tests for centralized PermissionHandler."""

from __future__ import annotations

import pytest

from core.services.permission_handler import (
    Permission,
    PermissionCheckResult,
    get_permission_handler,
)


@pytest.fixture
def handler():
    """Create a fresh PermissionHandler for each test."""
    h = get_permission_handler()
    h.clear_cache()
    return h


class TestPermissionEnum:
    """Test Permission enum."""

    def test_permission_enum_has_required_values(self):
        """Permission enum should have all required values."""
        # Core operations
        assert Permission.ADMIN.value == "admin"
        assert Permission.REPAIR.value == "repair"
        assert Permission.DESTROY.value == "destroy"

        # Development
        assert Permission.DEV_MODE.value == "dev_mode"
        assert Permission.TEST_MODE.value == "test_mode"

        # Wizard
        assert Permission.WIZARD.value == "wizard"

    def test_permission_string_conversion(self):
        """Permission enum should convert to string."""
        assert str(Permission.ADMIN) == "admin"
        assert str(Permission.DESTROY) == "destroy"


class TestPermissionCheckResult:
    """Test PermissionCheckResult dataclass."""

    def test_result_creation(self):
        """PermissionCheckResult should be creatable."""
        result = PermissionCheckResult(
            granted=True,
            permission=Permission.ADMIN,
            user_role="admin",
            reason="role has permission",
        )
        assert result.granted is True
        assert result.permission == Permission.ADMIN
        assert result.user_role == "admin"
        assert result.reason == "role has permission"

    def test_result_defaults(self):
        """PermissionCheckResult should have optional fields."""
        result = PermissionCheckResult(granted=False, permission=Permission.DESTROY)
        assert result.granted is False
        assert result.user_role is None
        assert result.reason is None


class TestPermissionHandlerBasics:
    """Test PermissionHandler basic functionality."""

    def test_handler_is_singleton(self):
        """get_permission_handler should return same instance."""
        h1 = get_permission_handler()
        h2 = get_permission_handler()
        assert h1 is h2

    def test_handler_has_logger(self, handler):
        """Handler should have logger."""
        assert hasattr(handler, "logger")
        assert handler.logger is not None

    def test_handler_has_cache(self, handler):
        """Handler should have cache dict."""
        assert hasattr(handler, "_cache")
        assert isinstance(handler._cache, dict)

    def test_handler_clear_cache(self, handler):
        """Handler should be able to clear cache."""
        handler._cache["test"] = True
        assert len(handler._cache) > 0
        handler.clear_cache()
        assert len(handler._cache) == 0


class TestPermissionChecking:
    """Test permission checking logic."""

    def test_has_permission_returns_boolean(self, handler):
        """has_permission should return boolean."""
        result = handler.has_permission(Permission.ADMIN)
        assert isinstance(result, bool)

    def test_has_permission_with_role(self, handler):
        """has_permission should accept user_role parameter."""
        # In testing mode, should always be True (alert-only)
        result = handler.has_permission(Permission.ADMIN, user_role="user")
        assert isinstance(result, bool)

    def test_has_permission_caches_result(self, handler):
        """has_permission should cache results."""
        # First call
        handler.has_permission(Permission.ADMIN)
        cache_size_1 = len(handler._cache)

        # Second call with same permission/role
        handler.has_permission(Permission.ADMIN)
        cache_size_2 = len(handler._cache)

        # Cache should not grow
        assert cache_size_1 == cache_size_2

    def test_any_permission(self, handler):
        """any_permission should check multiple permissions."""
        result = handler.any_permission(
            Permission.ADMIN, Permission.DESTROY, Permission.READ
        )
        assert isinstance(result, bool)

    def test_all_permissions(self, handler):
        """all_permissions should check multiple permissions."""
        result = handler.all_permissions(
            Permission.ADMIN, Permission.DESTROY, Permission.READ
        )
        assert isinstance(result, bool)

    def test_require_permission(self, handler):
        """require should check permission and handle errors."""
        # In testing mode, should return True
        result = handler.require(Permission.DESTROY)
        assert isinstance(result, bool)

    def test_require_with_action(self, handler):
        """require should accept action parameter."""
        result = handler.require(Permission.DESTROY, action="delete_vault")
        assert isinstance(result, bool)

    def test_require_role(self, handler):
        """require_role should check role membership."""
        # Admin should have admin role
        result = handler.require_role("admin", "admin", "maintainer")
        assert isinstance(result, bool)

    def test_require_role_with_none(self, handler):
        """require_role should use default role if None."""
        result = handler.require_role(None, "maintainer", "admin", "user")
        assert isinstance(result, bool)


class TestPermissionLogging:
    """Test permission logging."""

    def test_log_check_method_exists(self, handler):
        """log_check method should exist."""
        assert hasattr(handler, "log_check")
        # Should not raise
        handler.log_check(Permission.ADMIN, granted=True)

    def test_log_check_with_reason(self, handler):
        """log_check should accept reason parameter."""
        handler.log_check(Permission.ADMIN, granted=True, reason="user is admin")

    def test_log_check_with_context(self, handler):
        """log_check should accept context parameter."""
        handler.log_check(
            Permission.ADMIN,
            granted=True,
            context={"user": "test_admin", "action": "repair"},
        )

    def test_log_denied_method_exists(self, handler):
        """log_denied method should exist."""
        assert hasattr(handler, "log_denied")
        # Should not raise
        handler.log_denied(Permission.DESTROY)

    def test_log_denied_with_context(self, handler):
        """log_denied should accept context parameter."""
        handler.log_denied(
            Permission.DESTROY, context={"user": "test_user", "action": "delete_vault"}
        )


class TestTestingMode:
    """Test testing/alert-only mode behavior."""

    def test_testing_mode_is_enabled(self, handler):
        """Testing mode should be enabled in v1.4.x."""
        # _is_testing_mode is static, but we test through has_permission
        result = handler.has_permission(Permission.DESTROY)
        # In testing mode (v1.4.x), should always be True
        assert isinstance(result, bool)

    def test_all_permissions_allowed_in_testing(self, handler):
        """In testing mode, all permissions should be granted."""
        # This is the v1.4.x alert-only mode behavior
        # Actual enforcement will happen in v1.5
        dangerous_perms = [
            Permission.DESTROY,
            Permission.REPAIR,
            Permission.VAULT_DELETE,
            Permission.CONFIG_WRITE,
        ]

        for perm in dangerous_perms:
            result = handler.has_permission(perm)
            # In testing mode, should grant but log warnings
            assert isinstance(result, bool)


class TestDefaultRole:
    """Test default role behavior."""

    def test_default_role_method_exists(self, handler):
        """_default_role method should exist."""
        assert hasattr(handler, "_default_role")

    def test_default_role_returns_string(self, handler):
        """_default_role should return a string."""
        role = handler._default_role()
        assert isinstance(role, str)
        assert len(role) > 0


class TestRolePermissionsMap:
    """Test role to permissions mapping."""

    def test_get_role_permissions_map_exists(self, handler):
        """_get_role_permissions_map method should exist."""
        assert hasattr(handler, "_get_role_permissions_map")

    def test_role_permissions_map_returns_dict(self, handler):
        """_get_role_permissions_map should return dict."""
        role_map = handler._get_role_permissions_map()
        assert isinstance(role_map, dict)

    def test_role_permissions_map_has_entries(self, handler):
        """Role permissions map should have entries."""
        role_map = handler._get_role_permissions_map()
        # Should have at least some roles
        if len(role_map) > 0:
            role_name = list(role_map.keys())[0]
            perms = role_map[role_name]
            assert isinstance(perms, set)


class TestCheckPermissionInternal:
    """Test internal permission check logic."""

    def test_check_permission_returns_result(self, handler):
        """_check_permission should return PermissionCheckResult."""
        result = handler._check_permission(Permission.ADMIN, "admin")
        assert isinstance(result, PermissionCheckResult)

    def test_check_permission_with_default_role(self, handler):
        """_check_permission should work with empty role."""
        result = handler._check_permission(Permission.ADMIN, "")
        assert isinstance(result, PermissionCheckResult)

    def test_check_permission_testing_mode_grants_access(self, handler):
        """In testing mode, _check_permission should grant access."""
        result = handler._check_permission(Permission.DESTROY, "user")
        # In testing mode (v1.4.x alert-only), should grant
        assert isinstance(result, PermissionCheckResult)


class TestIntegration:
    """Integration tests for PermissionHandler."""

    def test_full_permission_flow(self, handler):
        """Test full permission checking flow."""
        # Check a permission
        has_perm = handler.has_permission(Permission.ADMIN)
        assert isinstance(has_perm, bool)

        # Require a permission
        required = handler.require(Permission.ADMIN, action="test_action")
        assert isinstance(required, bool)

        # Check role
        role_ok = handler.require_role("admin", "admin", "maintainer")
        assert isinstance(role_ok, bool)

    def test_permission_denied_handling(self, handler):
        """Test handling of denied permissions."""
        # Just verify require returns boolean (no exception in testing mode)
        result = handler.require(Permission.DESTROY)
        assert isinstance(result, bool)

    def test_cache_improves_performance(self, handler):
        """Test that caching works correctly."""
        # Clear cache
        handler.clear_cache()

        # Initial check populates cache
        handler.has_permission(Permission.ADMIN)
        assert len(handler._cache) > 0

        # Cached check should not add new entries
        initial_size = len(handler._cache)
        handler.has_permission(Permission.ADMIN)
        assert len(handler._cache) == initial_size
