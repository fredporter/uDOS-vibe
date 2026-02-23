#!/usr/bin/env python3
"""Cross-platform MCP activation manager for `.vibe/config.toml`."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import sys

BLOCK_BEGIN = "# BEGIN UCODE MANAGED MCP (WIZARD)"
BLOCK_END = "# END UCODE MANAGED MCP (WIZARD)"
MANAGED_BLOCK = """
# BEGIN UCODE MANAGED MCP (WIZARD)
[[mcp_servers]]
name = "wizard"
transport = "stdio"
command = "uv"
args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]
prompt = "uDOS Wizard MCP: ucode command dispatch, wizard services, system tooling"
startup_timeout_sec = 4.0
tool_timeout_sec = 25.0

  [mcp_servers.env]
  PYTHONPATH = "."
  WIZARD_MCP_REQUIRE_ADMIN_TOKEN = "0"
# END UCODE MANAGED MCP (WIZARD)
""".strip(
    "\n"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _config_path() -> Path:
    return _repo_root() / ".vibe" / "config.toml"


def _is_enabled(config_text: str) -> bool:
    return BLOCK_BEGIN in config_text and BLOCK_END in config_text


def _backup_config(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    backup = path.with_name(f"{path.name}.bak-{stamp}")
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup


def _remove_block(config_text: str) -> str:
    result_lines: list[str] = []
    skipping = False

    for line in config_text.splitlines():
        match line:
            case value if value == BLOCK_BEGIN:
                skipping = True
                continue
            case value if value == BLOCK_END:
                skipping = False
                continue
            case _:
                if not skipping:
                    result_lines.append(line)

    return "\n".join(result_lines).rstrip() + "\n"


def _enable(config_path: Path) -> int:
    config_text = config_path.read_text(encoding="utf-8")
    if _is_enabled(config_text):
        print("enabled")
        return 0

    backup = _backup_config(config_path)
    next_text = config_text.rstrip() + "\n\n" + MANAGED_BLOCK + "\n"
    config_path.write_text(next_text, encoding="utf-8")
    print(f"enabled (backup: {backup})")
    return 0


def _disable(config_path: Path) -> int:
    config_text = config_path.read_text(encoding="utf-8")
    if not _is_enabled(config_text):
        print("disabled")
        return 0

    backup = _backup_config(config_path)
    config_path.write_text(_remove_block(config_text), encoding="utf-8")
    print(f"disabled (backup: {backup})")
    return 0


def _status(config_path: Path) -> int:
    config_text = config_path.read_text(encoding="utf-8")
    print("enabled" if _is_enabled(config_text) else "disabled")
    return 0


def _contract() -> int:
    print(MANAGED_BLOCK)
    return 0


def main() -> int:
    parser = ArgumentParser(
        description="Manage the canonical Wizard MCP block in .vibe/config.toml.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="enable",
        choices=["enable", "disable", "status", "contract"],
        help="Action to run (default: enable).",
    )
    args = parser.parse_args()

    config_path = _config_path()
    if not config_path.exists():
        print(f"Missing config: {config_path}", file=sys.stderr)
        return 1

    match args.command:
        case "enable":
            return _enable(config_path)
        case "disable":
            return _disable(config_path)
        case "status":
            return _status(config_path)
        case "contract":
            return _contract()
        case _:
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
