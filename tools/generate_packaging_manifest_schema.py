"""Generate canonical packaging manifest v2 JSON schema."""

from __future__ import annotations

import json
from pathlib import Path

from core.services.packaging_manifest_models import PackagingManifestV2


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = repo_root / "distribution" / "schemas" / "packaging.manifest.v2.schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schema = PackagingManifestV2.model_json_schema(by_alias=True)
    output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()

