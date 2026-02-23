# M2.3 Doc Command Example Validation

Date: 2026-02-22

## Goal

Verify key active documentation command examples still match live CLI/dispatcher behavior.

## Validation Method

- Added regression test: `core/tests/docs_command_examples_contract_test.py`
- Test validates representative command examples from active roadmap/how-to docs:
  - `UCODE DEMO LIST`
  - `UCODE DEMO RUN sample-script`
  - `UCODE SYSTEM INFO`
  - `UCODE DOCS networking`
  - `UCODE UPDATE`
  - `UCODE CAPABILITIES --filter wizard`
  - `MODE STATUS`
  - `MODE THEME cyberpunk`
  - `PLAY LENS`
  - `FILE SELECT --file README.md`
- Each example must resolve in Stage 1 to expected top-level command with confidence `>= 0.8`.

## Test Run

- `uv run pytest core/tests/docs_command_examples_contract_test.py core/tests/v1_4_4_command_dispatch_chain_test.py -q`
- Result: 57 passed.

## Roadmap Update

- Marked complete:
  - `docs/roadmap.md` -> `M2.3 Quality Gates` -> "Verify command examples in docs match current CLI behavior."
