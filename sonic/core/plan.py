"""Plan and emit Sonic Screwdriver operations manifest."""

import argparse
from pathlib import Path
from typing import Dict, Optional

try:
    from .manifest import default_manifest, write_manifest
    from .os_limits import support_message, is_supported
except ImportError:  # pragma: no cover - fallback for direct execution
    from manifest import default_manifest, write_manifest
    from os_limits import support_message, is_supported


def build_plan(args: argparse.Namespace) -> Dict:
    repo_root = Path(args.repo_root).resolve()
    manifest = default_manifest(
        repo_root=repo_root,
        usb_device=args.usb_device,
        dry_run=args.dry_run,
        layout_path=Path(args.layout_file) if args.layout_file else None,
        format_mode=args.format_mode,
        payload_dir=Path(args.payloads_dir) if args.payloads_dir else None,
    )
    return manifest.to_dict()

def write_plan(
    repo_root: Path,
    usb_device: str,
    dry_run: bool,
    layout_path: Optional[Path],
    format_mode: Optional[str],
    payload_dir: Optional[Path],
    out_path: Path,
) -> Dict:
    manifest = default_manifest(
        repo_root,
        usb_device,
        dry_run,
        layout_path=layout_path,
        format_mode=format_mode,
        payload_dir=payload_dir,
    )
    write_manifest(out_path, manifest)
    return manifest.to_dict()


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sonic Screwdriver planner")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--usb-device", default="/dev/sdb")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default="config/sonic-manifest.json")
    parser.add_argument("--layout-file", default="config/sonic-layout.json")
    parser.add_argument(
        "--payloads-dir",
        default=None,
        help="Override payloads root directory (defaults to repo_root/payloads)",
    )
    parser.add_argument(
        "--format-mode",
        default=None,
        choices=["full", "skip"],
        help="Formatting mode for partitions (full|skip). Defaults to layout file or full.",
    )

    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    print(support_message())
    if not is_supported():
        print("ERROR Unsupported OS for build operations. Use Linux.")
        return 1

    out_path = Path(args.out)
    try:
        plan = write_plan(
            repo_root=Path(args.repo_root),
            usb_device=args.usb_device,
            dry_run=args.dry_run,
            layout_path=Path(args.layout_file) if args.layout_file else None,
            format_mode=args.format_mode,
            payload_dir=Path(args.payloads_dir) if args.payloads_dir else None,
            out_path=out_path,
        )
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1
    print(f"Plan written: {out_path}")
    if args.dry_run:
        print("Dry run enabled. No destructive operations should be executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
