from pathlib import Path

from core.tools.generate_grid_overlays_sample import build_sample_overlays
from core.commands.grid_handler import GridHandler


def test_grid_smoke_map_output(tmp_path: Path) -> None:
    payload = build_sample_overlays("EARTH:SUR:L305-DA11")
    input_path = tmp_path / "overlays.json"
    input_path.write_text(__import__("json").dumps(payload), encoding="utf-8")

    handler = GridHandler()
    result = handler.handle("GRID", ["MAP", "--input", str(input_path)], None, None)
    assert result.get("status") == "success"

    raw = result.get("grid_raw") or ""
    assert raw.startswith("--- udos-grid:v1")

    lines = raw.splitlines()
    try:
        start = lines.index("---") + 1
        end = lines.index("--- end ---")
    except ValueError:
        raise AssertionError("Missing grid body delimiters")

    body = lines[start:end]
    if body and body[0] == "":
        body = body[1:]
    if body and body[-1] == "":
        body = body[:-1]
    assert len(body) == 30
    assert all(len(line) == 80 for line in body)
