# M3.3 Boundary Enforcement Switch

Date: 2026-02-22

## Goal

Switch flagged runtime boundaries from advisory mode to enforced behavior for pre-launch readiness.

## Changes

- `core/services/mode_policy.py`
  - `boundaries_enforced()` now defaults to **on**.
  - Explicit opt-out remains available via:
    - `UDOS_ENFORCE_MODE_BOUNDARIES=0|false|no|off`
- `core/commands/sonic_handler.py`
  - `SONIC PLAN` and `SONIC RUN` now hard-restrict outside Wizard/Dev when boundaries are enforced.
  - Added explicit warning + `policy_flag=wizard_mode_required`.
- `core/commands/run_handler.py`
  - Updated policy note text for non-enforced edge case to reflect config-disabled enforcement.

## Test Updates

- `core/tests/mode_policy_test.py`
  - Updated default expectation to enforced by default.
  - Added explicit `off` override assertion.
- `core/tests/test_sonic_handler.py`
  - Added guard tests for `SONIC PLAN` and `SONIC RUN` restrictions when enforced.

## Validation

- `uv run pytest core/tests/mode_policy_test.py core/tests/run_handler_mode_guard_test.py core/tests/test_sonic_handler.py -q`
- Result: 12 passed.

## Roadmap Update

- Marked complete in `docs/roadmap.md`:
  - `M3.3` / "Enforce currently flagged runtime boundaries and behavior rules (pre-launch switch from flag-only to enforce)."
