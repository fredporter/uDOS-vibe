# uDOS-Vibe Dev Checklist

This checklist tracks implementation steps toward completion/release.
Execution model: `vibe-cli` runs looped command flow and returns shell commands for execution.

---

## Step 1: Execution Model Lock

- [ ] Confirm all interactive command handling routes through `vibe-cli`.
- [ ] Confirm shell-return command format is stable and safe.
- [ ] Remove remaining legacy runtime wording that conflicts with `vibe-cli` ownership.
- [ ] Verify fallback behavior: command match first, shell passthrough second, vibe/AI fallback last.
- [x] Implement selector-enabled command example with non-interactive fallback: `FILE SELECT`.

## Step 2: MCP and Tooling

- [ ] Validate single MCP gateway ownership in Wizard server.
- [ ] Ensure all required tools are registered and discoverable.
- [x] Add selector readiness gate for ucode command-set: `bin/check-ucode-selectors.sh`.
- [x] Publish selector readiness guide: `docs/howto/UCODE-SELECTOR-READINESS.md`.
- [ ] Verify skill routing for natural-language prompts and ambiguous intent.
- [ ] Add/confirm tests for tool invocation, routing, and typed errors.

## Step 3: Backend Completion

- [ ] Complete backend implementations for:
  - device
  - vault
  - workspace
  - automation
  - network diagnostics
  - script runner
  - user/auth
  - ask/language model routing
- [ ] Replace pending placeholders with production behavior.
- [ ] Add recovery-path tests for unavailable dependencies and malformed input.

## Step 4: Repo Structure and Cleanup

- [ ] Validate directory boundaries across `core/`, `wizard/`, and `extensions/`.
- [ ] Compost obsolete legacy-runtime planning/spec artifacts under `docs/.compost/`.
- [x] Publish selector standard for ucode command-set in `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md`.
- [ ] Remove duplicate or conflicting docs that describe deprecated interfaces.
- [ ] Verify examples and how-to docs align with current command flow.

## Step 5: Dependency and Runtime Health

- [ ] Run dependency checks via `uv` tooling only.
- [ ] Validate container build and runtime health for required components.
- [ ] Confirm no hidden environment assumptions in command paths.
- [ ] Verify reproducible local setup from documented instructions.

## Step 6: Release Gate

- [ ] Final command reference pass for consistency and correctness.
- [ ] Final docs pass to remove deprecated execution guidance.
- [ ] Confirm milestone completion criteria are met.
- [ ] Promote to release checklist and ship.
