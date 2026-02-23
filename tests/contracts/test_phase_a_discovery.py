#!/usr/bin/env python3
"""Phase A discovery smoke test for ucode tool modules."""

from __future__ import annotations


def test_tool_discovery() -> None:
    from vibe.core.tools.base import BaseTool
    from vibe.core.tools.ucode import content, data, spatial, system, workspace

    modules = {
        "system": system,
        "spatial": spatial,
        "data": data,
        "workspace": workspace,
        "content": content,
    }

    discovered: list[type[BaseTool]] = []
    for module in modules.values():
        for name in dir(module):
            if not name.startswith("Ucode"):
                continue
            candidate = getattr(module, name)
            if (
                isinstance(candidate, type)
                and issubclass(candidate, BaseTool)
                and candidate is not BaseTool
                and name not in {"UcodeResult", "UcodeConfig"}
            ):
                discovered.append(candidate)

    assert discovered, "Expected at least one ucode tool class to be discoverable"
