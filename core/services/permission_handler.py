"""Centralized Permission Handler

Unified permission checking system for both TUI and Wizard.
Integrates with UserManager for role-based access control.

**Design Principle:**
  Single source of truth for all permission decisions.
  No scattered permission checks across handlers.

**Usage:**
```python
from core.services.permission_handler import PermissionHandler, Permission

perms = PermissionHandler()

# Check if user has permission
if perms.has_permission(Permission.ADMIN):
    # User is admin
    pass

# Check multiple permissions
if perms.any_permission(Permission.REPAIR, Permission.ADMIN):
    # User can repair or is admin
    pass

# Require permission or alert (testing mode)
perms.require(Permission.DESTROY, action="delete_vault")

# Log permission check
perms.log_check(Permission.ADMIN, granted=True, context={"command": "DESTROY"})
```
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Centralized permission types for uDOS."""

    # Core operations
    ADMIN = "admin"  # Full system access
    REPAIR = "repair"  # Fix/heal system state
    DESTROY = "destroy"  # Irreversible operations (delete vault, factory reset)
    RESTORE = "restore"  # Restore from backups
    CONFIG = "config"  # Modify configuration

    # Development
    DEV_MODE = "dev_mode"  # Development features
    TEST_MODE = "test_mode"  # Test features
    HOT_RELOAD = "hot_reload"  # Hot reload system
    DEBUG = "debug"  # Debug features

    # Wizard/Services
    WIZARD = "wizard"  # Start/control Wizard server
    WIZARD_CONTROL = "wizard_control"  # Restart/reconfigure Wizard
    EXTENSION = "extension"  # Load/manage extensions
    PLUGIN = "plugin"  # Install plugins
    WEB = "web"  # Web access

    # Vault/Secrets
    VAULT_WRITE = "vault_write"  # Write to vault
    VAULT_DELETE = "vault_delete"  # Delete from vault
    SECRET_CREATE = "secret_create"  # Create secrets

    # User/Config
    USER_CREATE = "user_create"  # Create users
    USER_DELETE = "user_delete"  # Delete users
    CONFIG_WRITE = "config_write"  # Modify configuration

    # Data
    DATA_EXPORT = "data_export"  # Export user data
    DATA_IMPORT = "data_import"  # Import user data

    # File operations
    READ = "read"  # Read files/data
    WRITE = "write"  # Write files/data
    DELETE = "delete"  # Delete files/data

    # Gameplay
    GAMEPLAY_VIEW = "gameplay_view"  # View gameplay profile/stats
    GAMEPLAY_MUTATE = "gameplay_mutate"  # Update gameplay stats
    GAMEPLAY_GATE_ADMIN = "gameplay_gate_admin"  # Gate reset/override
    TOYBOX_LAUNCH = "toybox_launch"  # Launch runtime containers
    TOYBOX_ADMIN = "toybox_admin"  # Manage TOYBOX profile selection

    def __str__(self) -> str:
        return self.value


@dataclass
class PermissionCheckResult:
    """Result of a permission check."""

    granted: bool
    permission: Permission

    @staticmethod
    def _get_role_permissions_map() -> dict[str, set[Permission]]:
        """Return role to permissions mapping from UserManager.

        Returns:
            Dict mapping role names to sets of allowed permissions
        """
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        return {
            role.value: set(perms) for role, perms in user_mgr.ROLE_PERMISSIONS.items()
        }

    def all_permissions(
        self, *permissions: Permission, user_role: str | None = None
    ) -> bool:
        """Check if user has ALL of the given permissions.

        Args:
            permissions: Permissions to check (AND logic)
            user_role: Optional override of current user role

        Returns:
            True if user has all permissions
        """
        return all(self.has_permission(p, user_role) for p in permissions)

    def require(
        self,
        permission: Permission,
        action: str | None = None,
        raise_on_error: bool = False,
    ) -> bool:
        """Require permission for an action.

        In testing mode (alert-only), logs warning and returns True.
        In enforcement mode (future v1.5), raises or denies.

        Args:
            permission: Required permission
            action: Optional action description for logging
            raise_on_error: If True, raise PermissionError on denial

        Returns:
            True if granted, False if denied (in alert-only mode always True + logs)

        Raises:
            PermissionError: If raise_on_error=True and permission denied
        """
        granted = self.has_permission(permission)

        if not granted:
            context = {"action": action} if action else {}
            self.log_denied(permission, context)

            if raise_on_error:
                raise PermissionError(
                    f"Permission denied: {permission.value} for {action}"
                )

        return granted

    def require_role(self, role: str | None, *allowed: str) -> bool:
        """Require a specific role for access.

        Args:
            role: Role string (e.g., admin, maintainer)
            allowed: Allowed roles

        Returns:
            True if role is allowed, False otherwise
        """
        normalized_role = (role or "").strip().lower()
        if not normalized_role:
            normalized_role = self._default_role()

        allowed_roles = {r.strip().lower() for r in allowed if r}
        if not allowed_roles:
            return True

        granted = normalized_role in allowed_roles
        self.log_check(
            Permission.ADMIN,
            granted=granted,
            reason=f"role '{normalized_role}'",
            context={"allowed": sorted(allowed_roles)},
        )
        return granted

    def log_check(
        self,
        permission: Permission,
        granted: bool,
        reason: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log a permission check for audit trail.

        Args:
            permission: Permission checked
            granted: Whether permission was granted
            reason: Optional reason for decision
            context: Optional context dict (action, user_id, etc.)
        """
        context_str = f" | {context}" if context else ""
        level = "debug" if granted else "warning"
        msg = f"[PERMISSION] {permission.value}: {granted}{context_str}"
        if reason:
            msg += f" ({reason})"

        if level == "debug":
            self.logger.debug(msg)
        else:
            self.logger.warning(msg)

    def log_denied(
        self, permission: Permission, context: dict[str, Any] | None = None
    ) -> None:
        """Log a denied permission for audit trail.

        Args:
            permission: Permission denied
            context: Optional context dict
        """
        context_str = f" | {context}" if context else ""
        self.logger.warning(f"[PERMISSION_DENIED] {permission.value}{context_str}")

    def _check_permission(
        self, permission: Permission, user_role: str
    ) -> PermissionCheckResult:
        """Internal permission check logic.

        Uses role-based access control mapping.

        Args:
            permission: Permission to check
            user_role: User's role (admin, user, ghost, maintainer, etc.)

        Returns:
            PermissionCheckResult with granted status
        """
        from core.services.user_service import is_ghost_mode

        user_role = (user_role or "ghost").lower()

        # In testing mode (v1.4.x), all operations are allowed but logged
        is_testing = self._is_testing_mode()
        if is_testing:
            reason = "alert-only mode (v1.4.x testing)"
            return PermissionCheckResult(
                granted=True, permission=permission, user_role=user_role, reason=reason
            )

        # Role-based access control mapping
        role_permissions = self._get_role_permissions_map()
        allowed = role_permissions.get(user_role, set())

        # Check if user has the permission
        has_perm = permission in allowed

        # Special handling for ghost mode
        if not has_perm and is_ghost_mode():
            reason = "ghost mode active"
            return PermissionCheckResult(
                granted=False, permission=permission, user_role=user_role, reason=reason
            )

        if not has_perm:
            reason = f"role '{user_role}' does not have permission"
            return PermissionCheckResult(
                granted=False, permission=permission, user_role=user_role, reason=reason
            )

        return PermissionCheckResult(
            granted=True,
            permission=permission,
            user_role=user_role,
            reason=f"role '{user_role}' has permission",
        )

    @staticmethod
    def _get_role_permissions_map() -> dict[str, set[Permission]]:
        """Return role to permissions mapping from UserManager.

        Returns:
            Dict mapping role names to sets of allowed permissions
        """
        from core.services.user_service import get_user_manager

        user_mgr = get_user_manager()
        return {
            role.value: set(perms)
            for role, perms in user_mgr.ROLE_PERMISSIONS.items()
        }

    @staticmethod
    def _is_testing_mode() -> bool:
        """Check if in testing/alert-only mode (v1.4.x).

        In v1.4.x all restrictions are alert-only.
        Returns True during testing phase.

        Returns:
            True if in alert-only mode
        """
        from core.services.unified_config_loader import get_bool_config

        if get_bool_config("UDOS_TEST_MODE"):
            return True

        # v1.4.x is intentionally in testing/alert-only mode
        return True

    @staticmethod
    def _default_role() -> str:
        from core.services.unified_config_loader import get_config

        return get_config("UDOS_DEFAULT_ROLE", "maintainer").strip().lower()

    def clear_cache(self) -> None:
        """Clear permission check cache."""
        self._cache.clear()


# Singleton instance
_handler: PermissionHandler | None = None


def get_permission_handler() -> PermissionHandler:
    """Get singleton PermissionHandler instance.

    Returns:
        PermissionHandler singleton
    """
    global _handler
    if _handler is None:
        _handler = PermissionHandler()
    return _handler


# Convenience function
def check_permission(permission: Permission) -> bool:
    """Convenience wrapper to check permission.

    Args:
        permission: Permission to check

    Returns:
        True if permission granted
    """
    return get_permission_handler().has_permission(permission)
