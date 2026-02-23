import importlib
import json


def test_wizard_logging_wrapper_defaults_category_to_wizard_component(tmp_path, monkeypatch):
    monkeypatch.setenv("UDOS_LOG_ROOT", str(tmp_path))

    core_logging = importlib.import_module("core.services.logging_api")
    core_logging._LOG_MANAGER = None

    wizard_logging = importlib.import_module("wizard.services.logging_api")
    logger = wizard_logging.get_logger("wizard-only-category")
    logger.info("hello")

    files = list((tmp_path / "wizard").glob("wizard-*.jsonl"))
    assert files
    payload = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert payload["component"] == "wizard"
    assert payload["category"] == "wizard-only-category"
