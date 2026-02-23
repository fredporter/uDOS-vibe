# M3.2 Installation Guidance Validation (Core/Wizard/Sonic)

Date: 2026-02-22

## Goal

Verify installation and update guidance for Core, Wizard, and Sonic paths.

## Work Completed

- Updated `docs/INSTALLATION.md` profile guidance:
  - Core: `uv sync --extra udos`
  - Wizard web/API: `uv sync --extra udos-wizard` (FastAPI scope)
  - Full profile kept optional.

## Regression Coverage Added

- `core/tests/installation_guidance_paths_test.py`
  - Asserts Core/Wizard install/update commands are documented.
  - Asserts Sonic standalone release/install guide contains canonical build and readiness flow.

## Validation

- `uv run pytest core/tests/installation_guidance_paths_test.py core/tests/dependency_profile_separation_test.py core/tests/packaging_surface_contract_test.py -q`
- Result: 6 passed.

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.2` / "Verify installation and update guidance for Core, Wizard, and Sonic paths."
