# M3.3 Docs Consistency and Roadmap Guardrails

Date: 2026-02-22

## Goal

Advance final ship checklist with test-backed checks for user-facing command reference consistency and deprecated-architecture roadmap dependency guardrails.

## Work Completed

- Added user-facing command consistency test:
  - `core/tests/user_facing_command_reference_consistency_test.py`
  - Scans active docs command snippets and verifies tokens map to dispatcher command catalog or aliases.
- Added roadmap guardrail test:
  - `core/tests/roadmap_deprecated_architecture_dependency_test.py`
  - Ensures open roadmap items do not reference deprecated standalone/legacy TUI architecture dependencies.

## Validation

- `uv run pytest core/tests/user_facing_command_reference_consistency_test.py core/tests/docs_command_examples_contract_test.py core/tests/roadmap_deprecated_architecture_dependency_test.py -q`
- Result: 3 passed.

## Roadmap Update

- Marked complete in `docs/roadmap.md` (`M3.3 Final Ship Checklist`):
  - "Complete docs consistency pass for all user-facing command references."
  - "Verify no active roadmap items depend on deprecated TUI architecture."
