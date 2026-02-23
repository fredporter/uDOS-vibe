"""Guardrail: no active roadmap items should depend on deprecated TUI architecture."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_open_roadmap_items_do_not_reference_deprecated_tui_architecture() -> None:
    roadmap_lines = (REPO_ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8").splitlines()
    open_items = [line for line in roadmap_lines if line.strip().startswith("- [ ]")]

    forbidden_tokens = (
        "standalone tui",
        "legacy tui",
        "deprecated tui architecture",
    )
    for item in open_items:
        lower = item.lower()
        if "verify no active roadmap items depend on deprecated tui architecture" in lower:
            continue
        assert not any(token in lower for token in forbidden_tokens), item
