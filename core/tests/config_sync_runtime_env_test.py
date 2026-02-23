from __future__ import annotations

import json

from core.services.config_sync_service import ConfigSyncManager


def _mk_manager(tmp_path):
    manager = ConfigSyncManager()
    manager.repo_root = tmp_path
    manager.env_file = tmp_path / ".env"
    manager.env_file.parent.mkdir(parents=True, exist_ok=True)
    return manager


def test_resolve_runtime_value_precedence(monkeypatch, tmp_path):
    manager = _mk_manager(tmp_path)
    manager.env_file.write_text("VIBE_PRIMARY_PROVIDER=cloud\n")
    monkeypatch.setenv("VIBE_PRIMARY_PROVIDER", "local")
    assert manager.resolve_runtime_value("VIBE_PRIMARY_PROVIDER") == "local"


def test_hydrate_runtime_env_falls_back_to_user_state(monkeypatch, tmp_path):
    manager = _mk_manager(tmp_path)
    private_dir = tmp_path / "memory" / "bank" / "private"
    private_dir.mkdir(parents=True, exist_ok=True)
    (private_dir / "current_user.txt").write_text("ghost\n")
    (private_dir / "users.json").write_text(json.dumps({"ghost": {"role": "guest"}}))
    manager.env_file.write_text("")

    resolved = manager.hydrate_runtime_env(keys=["USER_NAME", "USER_ROLE"])
    assert resolved["USER_NAME"] == "ghost"
    assert resolved["USER_ROLE"] == "guest"
    assert resolved["USER_USERNAME"] == "ghost"
    assert resolved["UDOS_USER_ROLE"] == "guest"


def test_resolve_runtime_value_uses_secret_store_when_env_missing(monkeypatch, tmp_path):
    manager = _mk_manager(tmp_path)
    manager.env_file.write_text("")
    monkeypatch.setattr(
        manager,
        "_secret_store_env_lookup",
        lambda key: "secret-token" if key == "MISTRAL_API_KEY" else None,
    )
    assert manager.resolve_runtime_value("MISTRAL_API_KEY") == "secret-token"
