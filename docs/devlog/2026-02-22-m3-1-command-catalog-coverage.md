# M3.1 Command Catalog Coverage

Date: 2026-02-22

## Goal

Validate command catalog coverage between Stage 1 dispatch matching and the live TUI dispatcher command surface.

## Work Completed

- Reconciled Stage 1 command catalog in:
  - `core/services/command_dispatch_service.py`
- Aligned `UCODE_COMMANDS` to dispatcher-owned command names from `core/tui/dispatcher.py`.
- Added legacy token bridges for compatibility:
  - `RESTART` -> `REBOOT`
  - `SCHEDULE` -> `SCHEDULER`
  - `TALK` -> `SEND`

## Regression Coverage Added

- New test module:
  - `core/tests/command_catalog_coverage_test.py`
- Assertions:
  - Every dispatcher command is present in Stage 1 command catalog.
  - Legacy aliases route to canonical dispatcher commands with full confidence.

## Validation Run

- `uv run pytest core/tests/command_catalog_coverage_test.py core/tests/v1_4_4_command_dispatch_chain_test.py core/tests/docs_command_examples_contract_test.py -q`
- Result: 59 passed.

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.1` / "Validate command catalog coverage against actual dispatcher surface."
