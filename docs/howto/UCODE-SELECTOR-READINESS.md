# uCODE Selector Readiness

This guide validates selector and input-method readiness for the ucode command-set.

## Standard

Canonical selector contract:

- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md`

Execution model:

- Interactive flows through `vibe-cli`
- ucode commands must support non-interactive flags for automation

## Readiness Check

Run from repo root:

```bash
./bin/check-ucode-selectors.sh
```

The checker validates:

- Interactive terminal detection (TTY)
- Shell selector stack: `fzf`, `fd`, `gum`, `bat`
- Python selector stack: `PyInquirer`, `pick` (via `uv run python`)
- Fallback policy expectations

## Required vs Optional

- Required for selector-ready status:
  - `fzf`
- Recommended:
  - `fd`
  - `gum`
  - `bat`
  - `PyInquirer` (optional; may be incompatible on Python 3.12)
  - `pick`

## Input Method Contract

For each selector-enabled command:

1. Detect interactive mode (`isatty` / shell TTY).
2. If interactive and selector tooling exists, use selectors.
3. If selector tooling is unavailable, fallback to built-in menu/simple prompt.
4. Always support non-interactive flags (`--file`, `--files`, `--choice`, etc.).

## Acceptance Gate

A command-set is considered selector-ready when:

- `./bin/check-ucode-selectors.sh` reports no `FAIL`
- At least one command path demonstrates:
  - file picker flow
  - menu selector flow
  - multi-select flow
  - non-interactive fallback flow

Current reference command path:

```bash
FILE SELECT --workspace @sandbox
FILE SELECT --files readme.md,docs/roadmap.md
```

Note:
- If Ghost Mode is active, workspace access can be restricted by role policy.
- Run `SETUP` to exit Ghost Mode before validating workspace selectors.
