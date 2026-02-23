"""Boundary-safe networking checks for uCODE setup/cloud helpers."""

from __future__ import annotations

from core.services.stdlib_http import HTTPError
from core.tui.ucode import UCODE


class _LoggerStub:
    def debug(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, *_args, **_kwargs) -> None:
        return None

    def error(self, *_args, **_kwargs) -> None:
        return None


def _ucode_stub() -> UCODE:
    ucode = UCODE.__new__(UCODE)
    ucode.logger = _LoggerStub()
    ucode._env_file_cache = {}
    return ucode


def test_run_ok_cloud_maps_http_429_to_quota_message(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_wizard_headers", lambda: {})

    def _raise_429(*_args, **_kwargs):
        raise HTTPError(429, "Too Many Requests")

    monkeypatch.setattr("core.tui.ucode.http_post", _raise_429)

    result = ucode._run_ok_cloud("hello")
    assert result["model"] == "cloud-quota-exceeded"
    assert "quota exceeded" in result["response"].lower()


def test_run_ok_cloud_returns_wizard_offline_when_unreachable(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_wizard_headers", lambda: {})

    def _raise_offline(*_args, **_kwargs):
        raise HTTPError(0, "wizard offline")

    monkeypatch.setattr("core.tui.ucode.http_post", _raise_offline)

    result = ucode._run_ok_cloud("hello")
    assert result["model"] == "wizard-offline"
    assert "wizard cloud route unavailable" in result["response"].lower()


def test_run_ok_cloud_returns_error_when_chain_has_no_keys(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_wizard_headers", lambda: {})
    monkeypatch.setenv("VIBE_CLOUD_PROVIDER_CHAIN", "openai,anthropic")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def _fake_http_post(url: str, **_kwargs):
        if url.endswith("/api/ucode/ok/cloud"):
            raise HTTPError(0, "wizard offline")
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("core.tui.ucode.http_post", _fake_http_post)

    result = ucode._run_ok_cloud("hello")
    assert result["model"] == "wizard-offline"
    assert "web gate is closed in core" in result["response"].lower()


def test_run_ok_cloud_does_not_direct_fallback_when_primary_unreachable(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_wizard_headers", lambda: {})
    monkeypatch.setenv("VIBE_CLOUD_PROVIDER_CHAIN", "openai,anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "oa-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "an-key")

    def _fake_http_post(url: str, **_kwargs):
        if url.endswith("/api/ucode/ok/cloud"):
            raise HTTPError(0, "wizard offline")
        if "api.openai.com" in url:
            raise HTTPError(0, "connection refused")
        if "api.anthropic.com" in url:
            return {
                "status_code": 200,
                "json": {
                    "content": [{"type": "text", "text": "hello from anthropic"}]
                },
            }
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("core.tui.ucode.http_post", _fake_http_post)

    result = ucode._run_ok_cloud("hello")
    assert result["model"] == "wizard-offline"
    assert "wizard cloud route unavailable" in result["response"].lower()


def test_sync_mistral_secret_posts_encoded_query(monkeypatch) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setenv("WIZARD_ADMIN_TOKEN", "admin-token")
    calls: dict[str, object] = {}

    def _fake_http_post(url: str, headers=None, timeout=5, **_kwargs):
        calls["url"] = url
        calls["headers"] = headers or {}
        calls["timeout"] = timeout
        return {"status_code": 200, "json": {"ok": True}}

    monkeypatch.setattr("core.tui.ucode.http_post", _fake_http_post)
    ucode._sync_mistral_secret("abc 123")

    assert calls["url"] == "http://127.0.0.1:8765/api/settings-unified/secrets/mistral_api_key?value=abc%20123"
    assert calls["headers"] == {"Authorization": "Bearer admin-token"}


def test_fetch_or_generate_admin_token_uses_status_when_available(monkeypatch, tmp_path) -> None:
    ucode = _ucode_stub()
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(
        "core.tui.ucode.http_get",
        lambda url, **_kwargs: {"status_code": 200, "json": {"env": {"WIZARD_ADMIN_TOKEN": "wizard-token"}}},
    )

    token = ucode._fetch_or_generate_admin_token(tmp_path / ".env")
    assert token == "wizard-token"


def test_wizard_start_short_circuits_when_already_running(monkeypatch) -> None:
    ucode = _ucode_stub()
    ui_lines: list[tuple[str, str]] = []
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_run_with_progress", lambda _a, _b, fn, **_k: fn())
    monkeypatch.setattr(ucode, "_ui_line", lambda msg, level="info": ui_lines.append((level, msg)))
    status_type = type(
        "WizardStatus",
        (),
        {"connected": True, "message": "ok", "running": True, "pid": 1234},
    )
    manager = type(
        "WizardManager",
        (),
        {
            "status": staticmethod(lambda **_kwargs: status_type()),
            "ensure_running": staticmethod(lambda **_kwargs: status_type()),
        },
    )()
    monkeypatch.setattr("core.tui.ucode.get_wizard_process_manager", lambda: manager)

    ucode._wizard_start()
    assert ("ok", "Wizard already running") in ui_lines


def test_wizard_status_reports_not_running_on_connection_error(monkeypatch) -> None:
    ucode = _ucode_stub()
    ui_lines: list[tuple[str, str]] = []
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_run_with_progress", lambda _a, _b, fn, **_k: fn())
    monkeypatch.setattr(ucode, "_ui_line", lambda msg, level="info": ui_lines.append((level, msg)))

    def _raise_conn(*_a, **_k):
        raise HTTPError(0, "connection refused")

    monkeypatch.setattr("core.tui.ucode.http_get", _raise_conn)

    ucode._wizard_status()
    assert ("error", "Wizard not running") in ui_lines


def test_wizard_page_reports_http_status_failures(monkeypatch) -> None:
    ucode = _ucode_stub()
    ui_lines: list[tuple[str, str]] = []
    monkeypatch.setattr(ucode, "_wizard_base_url", lambda: "http://127.0.0.1:8765")
    monkeypatch.setattr(ucode, "_run_with_progress", lambda _a, _b, fn, **_k: fn())
    monkeypatch.setattr(ucode, "_ui_line", lambda msg, level="info": ui_lines.append((level, msg)))

    def _raise_not_found(*_a, **_k):
        raise HTTPError(404, "not found")

    monkeypatch.setattr("core.tui.ucode.http_get", _raise_not_found)

    ucode._wizard_page("ai")
    assert ("error", "Request failed: 404") in ui_lines
