from __future__ import annotations

from core.services.config_sync_service import ConfigSyncManager


def _mk_manager(tmp_path):
    manager = ConfigSyncManager()
    manager.repo_root = tmp_path
    manager.env_file = tmp_path / ".env"
    manager.env_file.parent.mkdir(parents=True, exist_ok=True)
    return manager


def test_sync_env_to_wizard_blocks_non_loopback_target(tmp_path):
    manager = _mk_manager(tmp_path)
    success, message = manager.sync_env_to_wizard("https://wizard.example.com/api/v1")
    assert success is False
    assert "Boundary policy" in message


def test_sync_env_to_wizard_posts_to_local_loopback(monkeypatch, tmp_path):
    manager = _mk_manager(tmp_path)
    token_path = tmp_path / "memory" / "bank" / "private" / "wizard_admin_token.txt"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text("test-token")
    monkeypatch.setattr(
        manager,
        "load_identity_from_env",
        lambda: {
            "user_username": "fred",
            "user_dob": "1990-01-01",
            "user_role": "user",
            "user_password": "pw",
            "user_location": "earth",
            "user_timezone": "UTC",
            "install_os_type": "linux",
        },
    )
    monkeypatch.setattr(
        "core.services.config_sync_service.guard_wizard_endpoint",
        lambda _path: None,
    )
    calls = {}

    def _fake_http_post(url: str, headers=None, json_data=None, timeout=5):
        calls["url"] = url
        calls["headers"] = headers or {}
        calls["json_data"] = json_data or {}
        calls["timeout"] = timeout
        return {"status_code": 200, "json": {"ok": True}}

    monkeypatch.setattr("core.services.config_sync_service.http_post", _fake_http_post)

    success, message = manager.sync_env_to_wizard("http://localhost:8765/api/v1")
    assert success is True
    assert "synced" in message.lower()
    assert calls["url"] == "http://localhost:8765/api/v1/setup/story/submit"
    assert calls["headers"]["Authorization"] == "Bearer test-token"
