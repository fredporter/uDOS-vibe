from __future__ import annotations

from core.services import mode_policy
from core.services.mode_policy import RuntimeMode


class _FakeUserManager:
    def __init__(self, can_dev: bool, is_admin: bool) -> None:
        self._can_dev = can_dev
        self._is_admin = is_admin

    def has_permission(self, permission) -> bool:
        if permission.value == "dev_mode":
            return self._can_dev
        if permission.value == "admin":
            return self._is_admin
        return False


def test_resolve_runtime_mode_ghost(monkeypatch):
    monkeypatch.setattr(mode_policy, "is_ghost_mode", lambda: True)
    monkeypatch.setattr(mode_policy, "get_dev_active", lambda: True)
    monkeypatch.setattr(mode_policy, "get_wizard_mode_active", lambda: True)
    monkeypatch.setattr(mode_policy, "get_user_manager", lambda: _FakeUserManager(can_dev=True, is_admin=True))
    assert mode_policy.resolve_runtime_mode() is RuntimeMode.GHOST


def test_resolve_runtime_mode_dev(monkeypatch):
    monkeypatch.setattr(mode_policy, "is_ghost_mode", lambda: False)
    monkeypatch.setattr(mode_policy, "get_dev_active", lambda: True)
    monkeypatch.setattr(mode_policy, "get_wizard_mode_active", lambda: False)
    monkeypatch.setattr(mode_policy, "get_user_manager", lambda: _FakeUserManager(can_dev=True, is_admin=True))
    assert mode_policy.resolve_runtime_mode() is RuntimeMode.DEV


def test_resolve_runtime_mode_wizard(monkeypatch):
    monkeypatch.setattr(mode_policy, "is_ghost_mode", lambda: False)
    monkeypatch.setattr(mode_policy, "get_dev_active", lambda: False)
    monkeypatch.setattr(mode_policy, "get_wizard_mode_active", lambda: True)
    monkeypatch.setattr(mode_policy, "get_user_manager", lambda: _FakeUserManager(can_dev=False, is_admin=True))
    assert mode_policy.resolve_runtime_mode() is RuntimeMode.WIZARD


def test_resolve_runtime_mode_user(monkeypatch):
    monkeypatch.setattr(mode_policy, "is_ghost_mode", lambda: False)
    monkeypatch.setattr(mode_policy, "get_dev_active", lambda: False)
    monkeypatch.setattr(mode_policy, "get_wizard_mode_active", lambda: False)
    monkeypatch.setattr(mode_policy, "get_user_manager", lambda: _FakeUserManager(can_dev=False, is_admin=False))
    assert mode_policy.resolve_runtime_mode() is RuntimeMode.USER


def test_user_mode_flags_external_tech_prompt(monkeypatch):
    monkeypatch.setattr(mode_policy, "resolve_runtime_mode", lambda: RuntimeMode.USER)
    assert mode_policy.user_mode_scope_flag("help me configure kubernetes cluster") == "user_mode_scope"
    assert mode_policy.user_mode_scope_flag("show sonic device compatibility") is None


def test_boundary_enforcement_toggle(monkeypatch):
    monkeypatch.delenv("UDOS_ENFORCE_MODE_BOUNDARIES", raising=False)
    assert mode_policy.boundaries_enforced() is True
    monkeypatch.setenv("UDOS_ENFORCE_MODE_BOUNDARIES", "off")
    assert mode_policy.boundaries_enforced() is False
    monkeypatch.setenv("UDOS_ENFORCE_MODE_BOUNDARIES", "1")
    assert mode_policy.boundaries_enforced() is True
