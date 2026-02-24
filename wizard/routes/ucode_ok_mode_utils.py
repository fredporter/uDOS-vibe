"""OK mode configuration/status helpers for uCODE routes."""

from __future__ import annotations

from typing import Any

from core.services.json_utils import read_json_file, write_json_file
from core.services.logging_api import get_repo_root
from core.services.unified_config_loader import get_bool_config

_OK_MODES_PATH_SEGMENTS = ("core", "config", "ok_modes.json")


def _ok_modes_path():
    return get_repo_root().joinpath(*_OK_MODES_PATH_SEGMENTS)


def load_ai_modes_config() -> dict[str, Any]:
    try:
        return read_json_file(_ok_modes_path(), default={"modes": {}})
    except Exception:
        return {"modes": {}}


def write_ok_modes_config(config: dict[str, Any]) -> None:
    write_json_file(_ok_modes_path(), config)


def is_dev_mode_active() -> bool:
    env_active = get_bool_config("UDOS_DEV_MODE", False)
    try:
        from wizard.services.dev_mode_service import get_dev_mode_service

        status = get_dev_mode_service().get_status()
        return bool(status.get("active")) or env_active
    except Exception:
        return env_active


def get_ok_default_models() -> dict[str, str]:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    default_models = mode.get("default_models") or {}
    core_model = default_models.get("core") or "mistral-small-latest"
    dev_model = (
        default_models.get("dev") or default_models.get("core") or "devstral-small-2"
    )
    return {"core": core_model, "dev": dev_model}


def get_ok_default_model(purpose: str = "general") -> str:
    models = get_ok_default_models()
    dev_active = is_dev_mode_active()
    if purpose == "coding" or dev_active:
        return models["dev"] if dev_active else models["core"]
    return models["core"]


def resolve_ok_model(requested_model: str | None, purpose: str = "general") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    return get_ok_default_model(purpose=purpose)


def ok_auto_fallback_enabled() -> bool:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    return bool(mode.get("auto_fallback", True))


def get_ok_context_window() -> int:
    try:
        from wizard.services.vibe_service import VibeConfig

        return VibeConfig().context_window
    except Exception:
        return 8192


def fetch_ollama_models(endpoint: str) -> dict[str, Any]:
    url = endpoint.rstrip("/") + "/api/tags"
    try:
        import requests

        resp = requests.get(url, timeout=2)
        if resp.status_code != 200:
            return {"reachable": False, "error": f"HTTP {resp.status_code}"}
        payload = resp.json()
        models = [m.get("name") for m in payload.get("models", []) if m.get("name")]
        return {"reachable": True, "models": models}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def _normalize_model_names(names: list[str]) -> set[str]:
    """Return canonical model names including both tagged and base forms."""
    normalized: set[str] = set()
    for raw in names:
        name = (raw or "").strip()
        if not name:
            continue
        normalized.add(name)
        base = name.split(":", 1)[0].strip()
        if base:
            normalized.add(base)
    return normalized


def get_ok_local_status() -> dict[str, Any]:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    endpoint = mode.get("ollama_endpoint", "http://127.0.0.1:11434")
    model = get_ok_default_model()
    tags = fetch_ollama_models(endpoint)
    if not tags.get("reachable"):
        return {
            "ready": False,
            "issue": "ollama down",
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": tags.get("error"),
            "models": [],
        }
    models = tags.get("models") or []
    normalized_models = _normalize_model_names(models)
    normalized_target = _normalize_model_names([model]) if model else set()
    if model and normalized_target.isdisjoint(normalized_models):
        return {
            "ready": False,
            "issue": "missing model",
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": None,
            "models": models,
        }
    return {
        "ready": True,
        "issue": None,
        "model": model,
        "ollama_endpoint": endpoint,
        "detail": None,
        "models": models,
    }


def get_ok_cloud_status() -> dict[str, Any]:
    try:
        from wizard.services.cloud_provider_executor import get_cloud_availability

        return get_cloud_availability()
    except Exception as exc:
        return {"ready": False, "issue": str(exc)}
