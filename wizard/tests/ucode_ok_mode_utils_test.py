from wizard.routes import ucode_ok_mode_utils as utils


def test_load_and_write_ai_modes_config(monkeypatch, tmp_path):
    from core.services import logging_api

    monkeypatch.setattr(logging_api, "get_repo_root", lambda: tmp_path)
    payload = {"modes": {"ofvibe": {"default_models": {"core": "x"}}}}
    utils.write_ok_modes_config(payload)
    loaded = utils.load_ai_modes_config()
    assert loaded["modes"]["ofvibe"]["default_models"]["core"] == "x"


def test_get_ok_default_model_respects_dev_mode(monkeypatch):
    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"default_models": {"core": "core-m", "dev": "dev-m"}}}},
    )
    monkeypatch.delenv("UDOS_DEV_MODE", raising=False)
    assert utils.get_ok_default_model() == "core-m"

    monkeypatch.setenv("UDOS_DEV_MODE", "true")
    assert utils.get_ok_default_model() == "dev-m"


def test_ok_auto_fallback_defaults_to_true(monkeypatch):
    monkeypatch.setattr(utils, "load_ai_modes_config", lambda: {"modes": {"ofvibe": {}}})
    assert utils.ok_auto_fallback_enabled() is True

    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"auto_fallback": False}}},
    )
    assert utils.ok_auto_fallback_enabled() is False


def test_get_ok_local_status_variants(monkeypatch):
    from unittest.mock import MagicMock

    from core.services.ai_provider_handler import ProviderStatus

    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"ollama_endpoint": "http://ollama"}}},
    )
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "model-a")

    def _handler(ps: ProviderStatus):
        h = MagicMock()
        h.check_local_provider.return_value = ps
        return h

    # Ollama unreachable → "ollama down"
    monkeypatch.setattr(
        utils,
        "get_ai_provider_handler",
        lambda: _handler(ProviderStatus(
            provider_id="ollama_local", is_configured=True, is_running=False,
            is_available=False, issue="ollama not running", loaded_models=[], default_model="model-a",
        )),
    )
    down = utils.get_ok_local_status()
    assert down["ready"] is False
    assert down["issue"] == "ollama down"

    # Running but required model absent → "missing model"
    monkeypatch.setattr(
        utils,
        "get_ai_provider_handler",
        lambda: _handler(ProviderStatus(
            provider_id="ollama_local", is_configured=True, is_running=True,
            is_available=False, issue="model not loaded: model-a", loaded_models=["other"], default_model="model-a",
        )),
    )
    missing = utils.get_ok_local_status()
    assert missing["ready"] is False
    assert missing["issue"] == "missing model"

    # Fully ready
    monkeypatch.setattr(
        utils,
        "get_ai_provider_handler",
        lambda: _handler(ProviderStatus(
            provider_id="ollama_local", is_configured=True, is_running=True,
            is_available=True, issue=None, loaded_models=["model-a"], default_model="model-a",
        )),
    )
    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None


def test_get_ok_local_status_accepts_tagged_alias(monkeypatch):
    from unittest.mock import MagicMock

    from core.services.ai_provider_handler import ProviderStatus

    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"ollama_endpoint": "http://ollama"}}},
    )
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "devstral-small-2")

    h = MagicMock()
    h.check_local_provider.return_value = ProviderStatus(
        provider_id="ollama_local", is_configured=True, is_running=True,
        is_available=True, issue=None,
        loaded_models=["devstral-small-2:latest"], default_model="devstral-small-2",
    )
    monkeypatch.setattr(utils, "get_ai_provider_handler", lambda: h)

    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None
