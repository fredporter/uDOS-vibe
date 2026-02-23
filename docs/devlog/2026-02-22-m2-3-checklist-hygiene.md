# M2.3 Checklist Hygiene Pass

Date: 2026-02-22

## Goal

Clear deprecated standalone-runtime wording from active roadmap/checklist surfaces and confirm consistency with the `vibe-cli` execution model.

## Updates

- Reworded active checklist/roadmap references from legacy standalone/TUI phrasing to neutral legacy-runtime phrasing:
  - `docs/roadmap.md`
  - `docs/vibe-todo.md`
- Updated active supporting docs to remove stale `TUI-only` wording:
  - `docs/features/alpine-core.md`
  - `docs/specs/typescript-markdown-runtime.md`

## Validation

- Audit command returned no matches for deprecated standalone wording in the updated active files:
  - `rg -n "standalone TUI|standalone uCODE|TUI-only|legacy TUI" docs/roadmap.md docs/vibe-todo.md docs/features/alpine-core.md docs/specs/typescript-markdown-runtime.md`

## Roadmap Status

- Marked complete:
  - `docs/roadmap.md` -> `M2.3 Quality Gates` -> "Confirm there are no references to deprecated standalone runtime workflows in active roadmap/checklists."
