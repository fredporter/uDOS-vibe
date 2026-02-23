# M3.1 Legacy Migration Notes Finalized

Date: 2026-02-22

## Goal

Finalize migration guidance for users coming from legacy standalone flows.

## Deliverables

- Added active migration guide:
  - `docs/howto/MIGRATION-NOTES-LEGACY-FLOWS.md`
- Linked migration guide from:
  - `docs/howto/UCODE-COMMAND-REFERENCE.md`

## Coverage

- Execution-model shift (`vibe-cli` first, fixed dispatch order).
- Canonical legacy alias bridges:
  - `RESTART` -> `REBOOT`
  - `SCHEDULE` -> `SCHEDULER`
  - `TALK` -> `SEND`
  - `UCLI` -> `UCODE`
  - `NEW`/`EDIT` -> `FILE` flows
- Operator checklist for script/doc migration.

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.1` / "Finalize migration notes for users coming from legacy flows."
