"""Generate dependency artifacts from canonical packaging manifest profiles."""

from __future__ import annotations

from pathlib import Path

from core.services.packaging_dependency_service import (
    render_apkbuild_dependency_snippet,
    render_dependency_docs_table,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    apkbuild_snippet = repo_root / "distribution" / "apkbuild" / "udos-ui" / "APKBUILD.depends.generated"
    docs_table = repo_root / "docs" / "features" / "packaging-dependency-map.md"

    apkbuild_snippet.parent.mkdir(parents=True, exist_ok=True)
    docs_table.parent.mkdir(parents=True, exist_ok=True)

    apkbuild_snippet.write_text(
        render_apkbuild_dependency_snippet(repo_root, profile="udos-ui-thin-gui"),
        encoding="utf-8",
    )
    docs_table.write_text(
        render_dependency_docs_table(repo_root),
        encoding="utf-8",
    )

    print(str(apkbuild_snippet))
    print(str(docs_table))


if __name__ == "__main__":
    main()
