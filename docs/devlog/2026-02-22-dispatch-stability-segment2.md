# Segment 2 Complete: Dispatch Stability (2026-02-22)

## Scope

Closed the dispatch-stability segment from `docs/roadmap.md` by fixing Stage 1/2/3 routing regressions and revalidating the command chain.

## Code Changes

### 1. Stage 1 command matching (`core/services/command_dispatch_service.py`)
- Added missing `PLACE` command to `UCODE_COMMANDS`.
- Restricted fuzzy matching to command-like tokens only:
  - token length >= 4
  - alphabetic tokens only
- This prevents shell-like inputs (`ls`, `nc`) from being incorrectly absorbed by Stage 1 fuzzy matching.

### 2. Stage 2 shell safety (`core/services/command_dispatch_service.py`)
- Tightened metacharacter rejection with `re.search` for shell chaining/substitution symbols.
- Strengthened dangerous-pattern checks (`rm -rf`, `/dev` redirects, command substitution).
- Restored expected rejection for injection forms like `cat file; rm important`.

### 3. Stage 3 skill inference (`core/services/command_dispatch_service.py`)
- Updated device patterns to include plural terms (`devices`, `machines`, etc.).
- Prioritized script inference for explicit script phrasing (including `automation script`).
- Reduced wizard over-capture by narrowing wizard keywords/patterns.
- Reduced vault over-capture for generic password-reset phrasing, preserving `ask` fallback.

## Validation

### Dispatch-chain suite
```bash
uv run pytest core/tests/v1_4_4_command_dispatch_chain_test.py -q
```
- Result: `49 passed, 0 failed`

### Combined checkpoint suite
```bash
uv run pytest core/tests/ucode_min_spec_command_test.py core/tests/v1_4_4_command_dispatch_chain_test.py -q
```
- Result: `58 passed, 0 failed`

## Roadmap Update

Updated `docs/roadmap.md`:
- Segment 2 checklist marked complete for all four items.

