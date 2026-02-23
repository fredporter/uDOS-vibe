"""Sonic Screwdriver manifest utilities."""

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class PartitionSpec:
    name: str
    label: str
    fs: str
    size_gb: Optional[float] = None
    remainder: bool = False
    mount: Optional[str] = None
    format: bool = True
    flags: List[str] = field(default_factory=list)
    role: Optional[str] = None
    scalable: bool = False
    min_size_gb: Optional[float] = None
    max_size_gb: Optional[float] = None
    image: Optional[str] = None
    payload_dir: Optional[str] = None


@dataclass
class SonicManifest:
    usb_device: str
    boot_mode: str
    repo_root: str
    payload_dir: str
    iso_dir: str
    flash_label: str = "FLASH"
    sonic_label: str = "SONIC"
    esp_label: str = "ESP"
    dry_run: bool = False
    format_mode: str = "full"
    auto_scale: bool = False
    partitions: List[PartitionSpec] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        return data


def write_manifest(path: Path, manifest: SonicManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2))


def read_manifest(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _default_partitions() -> List[PartitionSpec]:
    return [
        PartitionSpec(name="esp", label="ESP", fs="fat32", size_gb=0.5, flags=["boot", "esp"], role="efi"),
        PartitionSpec(name="udos_ro", label="UDOS_RO", fs="squashfs", size_gb=8, role="udos"),
        PartitionSpec(name="udos_rw", label="UDOS_RW", fs="ext4", size_gb=8, mount="/mnt/udos", role="udos"),
        PartitionSpec(name="swap", label="SWAP", fs="swap", size_gb=8, role="swap"),
        PartitionSpec(name="wizard", label="WIZARD", fs="ext4", size_gb=20, mount="/mnt/wizard", role="wizard"),
        PartitionSpec(name="win10", label="WIN10", fs="ntfs", size_gb=48, role="windows"),
        PartitionSpec(name="media", label="MEDIA", fs="exfat", size_gb=28, mount="/mnt/media", role="media"),
        PartitionSpec(name="cache", label="CACHE", fs="ext4", remainder=True, mount="/mnt/cache", role="cache"),
    ]

def validate_partitions(partitions: List[PartitionSpec]) -> None:
    remainder_count = sum(1 for p in partitions if p.remainder)
    if remainder_count > 1:
        raise ValueError("Only one remainder partition is allowed.")
    for p in partitions:
        if p.remainder:
            continue
        if p.size_gb is None or p.size_gb <= 0:
            raise ValueError(f"Partition '{p.name}' must define a positive size_gb.")

def _load_partitions(layout_path: Optional[Path]) -> List[PartitionSpec]:
    if not layout_path:
        return _default_partitions()
    if not layout_path.exists():
        return _default_partitions()
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return _default_partitions()
    partitions = []
    for item in data.get("partitions", []):
        partitions.append(
            PartitionSpec(
                name=item.get("name", ""),
                label=item.get("label", ""),
                fs=item.get("fs", ""),
                size_gb=item.get("size_gb"),
                remainder=item.get("remainder", False),
                mount=item.get("mount"),
                format=item.get("format", True),
                flags=item.get("flags", []),
                role=item.get("role"),
                scalable=item.get("scalable", False),
                min_size_gb=item.get("min_size_gb"),
                max_size_gb=item.get("max_size_gb"),
                image=item.get("image"),
                payload_dir=item.get("payload_dir"),
            )
        )
    return partitions or _default_partitions()


def _load_format_mode(layout_path: Optional[Path]) -> Optional[str]:
    if not layout_path or not layout_path.exists():
        return None
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return None
    mode = data.get("format_mode")
    if mode in {"full", "skip"}:
        return mode
    return None


def _load_auto_scale(layout_path: Optional[Path]) -> Optional[bool]:
    if not layout_path or not layout_path.exists():
        return None
    try:
        data = json.loads(layout_path.read_text())
    except json.JSONDecodeError:
        return None
    if "auto_scale" in data:
        return bool(data.get("auto_scale"))
    return None


def default_manifest(
    repo_root: Path,
    usb_device: str,
    dry_run: bool,
    layout_path: Optional[Path] = None,
    format_mode: Optional[str] = None,
    payload_dir: Optional[Path] = None,
) -> SonicManifest:
    resolved_payload_dir = payload_dir or (repo_root / "payloads")
    iso_dir = repo_root / "ISOS"
    resolved_format = format_mode or _load_format_mode(layout_path) or "full"
    resolved_auto_scale = _load_auto_scale(layout_path) or False
    partitions = _load_partitions(layout_path)
    validate_partitions(partitions)
    return SonicManifest(
        usb_device=usb_device,
        boot_mode="uefi-native",
        repo_root=str(repo_root),
        payload_dir=str(resolved_payload_dir),
        iso_dir=str(iso_dir),
        dry_run=dry_run,
        format_mode=resolved_format,
        auto_scale=resolved_auto_scale,
        partitions=partitions,
    )
