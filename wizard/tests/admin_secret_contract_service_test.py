from __future__ import annotations

import json

import wizard.services.admin_secret_contract as contract
from wizard.services.secret_store import SecretStoreError


class _LockedStore:
    def unlock(self, _key=None) -> None:
        raise SecretStoreError("locked")

    def get_entry(self, _key_id):
        return None


class _MemoryStore:
    def __init__(self) -> None:
        self.entries: dict[str, object] = {}
        self.unlocked = False

    def unlock(self, _key=None) -> None:
        self.unlocked = True

    def get_entry(self, key_id):
        return self.entries.get(key_id)

    def set(self, entry) -> None:
        self.entries[entry.key_id] = entry


class _AlwaysLockedStore:
    def unlock(self, _key=None) -> None:
        raise SecretStoreError("locked tomb")

    def get_entry(self, _key_id):
        return None


def test_collect_admin_secret_contract_detects_drift(monkeypatch, tmp_path) -> None:
    (tmp_path / "wizard" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "wizard" / "config" / "wizard.json").write_text("{}", encoding="utf-8")
    monkeypatch.delenv("WIZARD_KEY", raising=False)
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)
    monkeypatch.setattr(contract, "get_secret_store", lambda: _LockedStore())

    status = contract.collect_admin_secret_contract(repo_root=tmp_path)

    assert status["ok"] is False
    assert "missing_wizard_key" in status["drift"]
    assert "missing_admin_api_key_id" in status["drift"]
    assert "missing_admin_token" in status["drift"]
    assert "secret_store_locked" in status["drift"]


def test_repair_admin_secret_contract_syncs_env_config_and_secret(monkeypatch, tmp_path) -> None:
    (tmp_path / "wizard" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "wizard" / "config" / "wizard.json").write_text("{}", encoding="utf-8")
    store = _MemoryStore()
    monkeypatch.setattr(contract, "get_secret_store", lambda: store)
    monkeypatch.delenv("WIZARD_KEY", raising=False)
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)

    result = contract.repair_admin_secret_contract(repo_root=tmp_path)

    assert result["repaired"] is True
    env_text = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "WIZARD_KEY=" in env_text
    assert "WIZARD_ADMIN_TOKEN=" in env_text

    config = json.loads((tmp_path / "wizard" / "config" / "wizard.json").read_text(encoding="utf-8"))
    assert config["admin_api_key_id"] == "wizard-admin-token"
    assert store.get_entry("wizard-admin-token") is not None
    assert result["status_after"]["ok"] is True


def test_repair_admin_secret_contract_recovers_locked_store(monkeypatch, tmp_path) -> None:
    (tmp_path / "wizard" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "wizard" / "config" / "wizard.json").write_text("{}", encoding="utf-8")
    locked = _AlwaysLockedStore()
    healthy = _MemoryStore()
    calls = {"count": 0}

    def _store_factory():
        calls["count"] += 1
        if calls["count"] <= 2:
            return locked
        return healthy

    monkeypatch.setattr(contract, "get_secret_store", _store_factory)
    monkeypatch.delenv("WIZARD_KEY", raising=False)
    monkeypatch.delenv("WIZARD_ADMIN_TOKEN", raising=False)

    result = contract.repair_admin_secret_contract(repo_root=tmp_path)

    assert result["repaired"] is True
    assert result["recovery_mode"] == "secret_store_reset"
    assert "secret_store_locked" in result["status_before"]["drift"]
    assert result["status_after"]["ok"] is True
    assert healthy.get_entry("wizard-admin-token") is not None
