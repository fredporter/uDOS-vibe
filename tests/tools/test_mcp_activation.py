from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_mcp_activation_module() -> object:
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "mcp_activation.py"
    spec = importlib.util.spec_from_file_location("mcp_activation", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_enable_disable_contract_block_is_managed(monkeypatch, tmp_path):
    module = _load_mcp_activation_module()
    config_dir = tmp_path / ".vibe"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    config_path.write_text("active_model = \"devstral-small\"\n", encoding="utf-8")
    monkeypatch.setattr(module, "_repo_root", lambda: tmp_path)

    assert module._enable(config_path) == 0
    enabled_text = config_path.read_text(encoding="utf-8")
    assert module.BLOCK_BEGIN in enabled_text
    assert module.BLOCK_END in enabled_text
    enable_backups = list(config_dir.glob("config.toml.bak-*"))
    assert len(enable_backups) == 1

    assert module._enable(config_path) == 0
    assert len(list(config_dir.glob("config.toml.bak-*"))) == 1

    assert module._disable(config_path) == 0
    disabled_text = config_path.read_text(encoding="utf-8")
    assert module.BLOCK_BEGIN not in disabled_text
    assert module.BLOCK_END not in disabled_text
    assert len(list(config_dir.glob("config.toml.bak-*"))) == 2


def test_status_and_contract_output(monkeypatch, tmp_path, capsys):
    module = _load_mcp_activation_module()
    config_dir = tmp_path / ".vibe"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    config_path.write_text("active_model = \"devstral-small\"\n", encoding="utf-8")
    monkeypatch.setattr(module, "_repo_root", lambda: tmp_path)

    assert module._status(config_path) == 0
    assert capsys.readouterr().out.strip() == "disabled"

    assert module._enable(config_path) == 0
    capsys.readouterr()
    assert module._status(config_path) == 0
    assert capsys.readouterr().out.strip() == "enabled"

    assert module._contract() == 0
    contract_output = capsys.readouterr().out
    assert module.BLOCK_BEGIN in contract_output
    assert module.BLOCK_END in contract_output
    assert "command = \"uv\"" in contract_output
