# M2.1 Boundary Validation

Date: 2026-02-22

## Scope

- Milestone 2.1 boundary verification for canonical runtime layout:
  - `core/` is the reusable runtime and command surface.
  - `wizard/` remains the MCP/admin orchestration surface.
  - `extensions/` remains the optional module surface.

## Validation Added

- Added boundary test module: `core/tests/repo_structure_boundaries_test.py`.
- Assertions cover:
  - Expected `core` runtime directories (`commands`, `services`, `tui`).
  - Canonical MCP gateway files under `wizard/mcp/`.
  - Guardrail against accidental duplicate MCP entrypoints under `core/mcp` or `extensions/mcp`.
  - Presence of at least one extension package under `extensions/`.

## Result

- Boundary checks pass in CI-style local run through `uv`:
  - `uv run pytest core/tests/repo_structure_boundaries_test.py -q`
- Roadmap checkbox updated:
  - `docs/roadmap.md` -> `M2.1 Structure Validation` / `Verify boundaries` marked complete.
