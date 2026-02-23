import importlib
import json


def test_logging_api_writes_jsonl(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))

    logging_api = importlib.import_module("core.services.logging_api")
    logging_api._LOG_MANAGER = None

    logger = logging_api.get_logger("core", category="test", name="core")
    logger.info("hello", ctx={"foo": "bar", "password": "secret"})

    log_dir = tmp_path / "core"
    files = list(log_dir.glob("core-*.jsonl"))
    assert files

    last_line = files[0].read_text(encoding="utf-8").strip().splitlines()[-1]
    payload = json.loads(last_line)

    assert payload["level"] == "info"
    assert payload["component"] == "core"
    assert payload["category"] == "test"
    assert payload["event"]
    assert payload["ctx"]["foo"] == "bar"
    assert payload["ctx"]["password"] == "[REDACTED]"


def test_logging_api_backward_compatibility_defaults_to_core_component(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))

    logging_api = importlib.import_module("core.services.logging_api")
    logging_api._LOG_MANAGER = None

    logger = logging_api.get_logger("my-category")
    logger.info("hello")

    files = list((tmp_path / "core").glob("core-*.jsonl"))
    assert files
    payload = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert payload["component"] == "core"
    assert payload["category"] == "my-category"


def test_logging_api_exception_alias_captures_error_stack(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))

    logging_api = importlib.import_module("core.services.logging_api")
    logging_api._LOG_MANAGER = None

    logger = logging_api.get_logger("core", category="test", name="core")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("captured error")

    files = list((tmp_path / "core").glob("core-*.jsonl"))
    assert files
    payload = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert payload["level"] == "error"
    assert payload["msg"] == "captured error"
    assert payload["err"]["stack"]
