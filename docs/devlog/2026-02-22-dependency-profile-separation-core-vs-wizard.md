# Dependency Profile Separation: Core vs Wizard

Date: 2026-02-22

## Goal

Ensure GUI/web dependencies (FastAPI) stay scoped to Wizard profiles and are not required for Core/MCP workflows.

## Changes

- Added dependency contract test:
  - `core/tests/dependency_profile_separation_test.py`
- Test assertions:
  - `fastapi` is **not** present in base dependencies.
  - `fastapi` is present in Wizard dependency profiles:
    - `pyproject.toml` -> `project.optional-dependencies.udos-wizard`
    - `pyproject.udos.toml` -> `project.optional-dependencies.wizard`

## Documentation Update

- Updated `docs/INSTALLATION.md` to use profile-specific sync commands:
  - `uv sync --extra udos` for Core
  - `uv sync --extra udos-wizard` for Wizard web/API (FastAPI)
  - `udos-full` remains optional

## Validation

- `uv run pytest core/tests/dependency_profile_separation_test.py -q`
- Result: 2 passed.
