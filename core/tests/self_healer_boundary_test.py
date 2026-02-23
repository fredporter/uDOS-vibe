from __future__ import annotations

from urllib.error import URLError

from core.services.self_healer import SelfHealer


def test_sanitize_loopback_ollama_host_accepts_localhost() -> None:
    healer = SelfHealer(component="core", auto_repair=False)
    assert (
        healer._sanitize_loopback_ollama_host("http://localhost:11434")
        == "http://localhost:11434"
    )


def test_sanitize_loopback_ollama_host_blocks_non_loopback() -> None:
    healer = SelfHealer(component="core", auto_repair=False)
    assert healer._sanitize_loopback_ollama_host("https://ollama.example.com") == ""


def test_check_ollama_default_model_adds_missing_model_issue(monkeypatch) -> None:
    class _Response:
        status = 200

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def read(self) -> bytes:
            return b'{"models":[{"name":"mistral:latest"}]}'

    monkeypatch.setenv("OLLAMA_DEFAULT_MODEL", "devstral-small-2")
    monkeypatch.setattr("core.services.self_healer.urllib.request.urlopen", lambda *_args, **_kwargs: _Response())

    healer = SelfHealer(component="core", auto_repair=False)
    healer._check_ollama_default_model("http://127.0.0.1:11434")

    issue = next((item for item in healer.issues if item.repair_action == "pull_ollama_model"), None)
    assert issue is not None
    assert issue.details["model"] == "devstral-small-2"


def test_check_ollama_default_model_skips_when_tags_unreachable(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_DEFAULT_MODEL", "devstral-small-2")
    monkeypatch.setattr(
        "core.services.self_healer.urllib.request.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("offline")),
    )

    healer = SelfHealer(component="core", auto_repair=False)
    healer._check_ollama_default_model("http://127.0.0.1:11434")
    assert healer.issues == []
