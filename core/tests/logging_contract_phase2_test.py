from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys


def _reset_log_manager():
    logging_api = importlib.import_module("core.services.logging_api")
    logging_api._LOG_MANAGER = None
    return logging_api


def test_server_modular_source_uses_core_logging_contract():
    path = Path("distribution/plugins/api/server_modular.py")
    text = path.read_text(encoding="utf-8")
    assert "from core.services.logging_api import get_logger" in text
    assert "api_logger = get_logger(" in text
    assert "RotatingFileHandler" not in text
    assert "logging.basicConfig" not in text


def test_vibe_utils_source_avoids_rotating_file_handlers():
    path = Path("vibe/core/utils.py")
    text = path.read_text(encoding="utf-8")
    assert "RotatingFileHandler" not in text


def test_vibe_utils_routes_logs_to_core_jsonl_sink(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))
    _reset_log_manager()

    if "vibe.core.utils" in sys.modules:
        del sys.modules["vibe.core.utils"]
    utils = importlib.import_module("vibe.core.utils")

    utils.logger.info("contract-check", ctx={"test": "vibe"})

    files = list((tmp_path / "core").glob("vibe-*.jsonl"))
    assert files
    payload = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert payload["component"] == "core"
    assert payload["category"] == "vibe"
    assert payload["msg"] == "contract-check"


def test_input_command_prompt_uses_core_logging_contract_only():
    path = Path("core/input/command_prompt.py")
    text = path.read_text(encoding="utf-8")
    assert "logging.getLogger(" not in text
    assert "StreamHandler(" not in text
    assert "logging.basicConfig" not in text


def test_input_keypad_handler_uses_core_logging_contract_only():
    path = Path("core/input/keypad_handler.py")
    text = path.read_text(encoding="utf-8")
    assert "logging.getLogger(" not in text
    assert "StreamHandler(" not in text
    assert "logging.basicConfig" not in text
