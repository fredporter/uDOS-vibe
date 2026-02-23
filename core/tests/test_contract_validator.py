import json
from pathlib import Path

from core.tools.contract_validator import (
    validate_theme_pack,
    validate_vault_contract,
    validate_world_contract,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_theme_pack_success(tmp_path: Path) -> None:
    theme_dir = tmp_path / "themes" / "prose"
    (theme_dir / "assets").mkdir(parents=True)
    _write(theme_dir / "shell.html", "<!DOCTYPE html><html><body>{{content}}{{title}}{{nav}}{{meta}}{{footer}}</body></html>")
    _write(theme_dir / "theme.css", "body { font-family: serif; }")
    _write(
        theme_dir / "theme.json",
        json.dumps(
            {
                "name": "prose",
                "version": "1.0.0",
                "mode": "article",
                "slots": ["{{content}}", "{{title}}", "{{nav}}", "{{meta}}", "{{footer}}"],
            }
        ),
    )

    report = validate_theme_pack(theme_dir)
    assert report.valid


def test_validate_vault_contract_missing_md(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    report = validate_vault_contract(vault_dir)
    assert not report.valid
    assert any("Markdown" in err for err in report.errors)


def test_validate_world_contract_locid(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    _write(vault_dir / "note.md", "Invalid L999-ZZ99 and EARTH:SUR:L305-DA11")
    report = validate_world_contract(vault_dir)
    assert not report.valid
    assert report.details.get("invalid_locids")
