# M1.1 Progress: Dispatch Diagnostics + Deterministic Shell Payloads (2026-02-22)

## Scope

Advanced Milestone 1.1 by implementing:
- diagnostics visibility for dispatch stage decisions/failures
- deterministic, auditable shell payload metadata on Stage 2 shell routing

## Implementation

Updated:
- `core/services/command_dispatch_service.py`

### Diagnostics mode

`--dispatch-debug` now includes a stable `debug.route_trace` list with stage-level decisions:
- Stage 1 match/dispatch decision
- Stage 2 validation/skip/dispatch decision (including failure reason)
- Stage 3 fallback dispatch decision

### Deterministic shell payload

On Stage 2 shell dispatch, response now includes `shell` metadata:
- `command`
- `args`
- `raw`
- `validation_reason`
- `allowlist_enabled`
- `blocklist_enabled`
- `requires_confirmation` (currently `false`)

This provides a consistent surface for auditing and future policy hooks.

## Tests

Updated:
- `core/tests/v1_4_4_command_dispatch_chain_test.py`

Added coverage for:
- shell payload structure on safe shell route
- route trace content in debug mode
- Stage 2 validation-failure trace
- Stage 2 shell-disabled skip trace

Validation command:

```bash
uv run pytest core/tests/v1_4_4_command_dispatch_chain_test.py -q
```

Result:
- `51 passed, 0 failed`

## Roadmap Updates

Updated `docs/roadmap.md` under M1.1:
- marked complete: deterministic shell payloads
- marked complete: diagnostics mode

Follow-up completion (same day):
- locked dispatch response contract metadata (`contract.version = m1.1`, route order fixed to `ucode -> shell -> vibe`)
- added explicit Stage 2 shell confirmation gate for non-read-only commands (`dispatch_to = confirm`, `status = pending`)

M1.1 status:
- complete
