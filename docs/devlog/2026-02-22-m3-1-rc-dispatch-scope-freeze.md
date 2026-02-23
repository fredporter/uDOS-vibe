# M3.1 RC Dispatch Scope Freeze

Date: 2026-02-22

## Goal

Freeze command syntax and fallback behavior for release-candidate scope.

## Deliverables

- Added spec:
  - `docs/specs/COMMAND-DISPATCH-RC-SCOPE.md`
- Added RC contract tests:
  - `core/tests/dispatch_rc_scope_contract_test.py`

## Scope Locked

- Dispatch route order remains:
  - `ucode` -> `shell` -> `vibe`
- Canonical alias bridges frozen:
  - `RESTART` -> `REBOOT`
  - `SCHEDULE` -> `SCHEDULER`
  - `TALK` -> `SEND`
- Existing command-entry aliases retained:
  - `NEW`/`EDIT` -> `FILE`
  - `UCLI` -> `UCODE`

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.1` / "Freeze command syntax and fallback behavior for release candidate scope."
