# Terminal Text Operations Decision (v1.4)

## Status

Active. Supersedes the earlier Wizard-dashboard CSS-oriented terminal styling decision.

## Context

The previous decision focused on Wizard GUI component styling. That is no longer the right scope for terminal behavior in uDOS.

Current need:

- consistent text-first TUI behavior for `vibe` and regular shell usage
- reusable file picker/selector/input/output handlers
- deterministic output contracts for command handlers and scripts

## Scope

This decision applies to text-mode terminal interactions in Core and Vibe command flows:

- interactive file pickers and selectors
- command input prompts and menu/select flows
- terminal output formatting (plain text and optional ANSI)
- shell-safe non-interactive output

This decision does **not** define Wizard GUI visual styles.

## Decision

### 1. Separate TUI text operations from Wizard GUI

- TUI text operations are Core runtime behavior.
- Wizard dashboard styling is a separate frontend concern.
- No Wizard CSS tokens/classes are normative for terminal flows.

### 2. Standardize terminal interaction modes

- **Interactive TTY mode**:
  - prefer selector/picker UX (menus, file pickers, key navigation)
  - use TTY detection before interactive flows
- **Non-interactive mode**:
  - require flag-based inputs (`--file`, `--files`, `--choice`, etc.)
  - outputs must remain script-safe and parseable

### 3. Standardize output tiers

- **Plain text** is canonical for terminal compatibility.
- **ANSI text** is optional enhancement only; width/layout must remain correct without ANSI.
- **Structured result dict/json** remains source-of-truth for automation and wrappers.

### 4. Reuse existing Core TUI primitives

Primary building blocks:

- `core/tui/output.py` (`OutputToolkit`) for banners/tables/text blocks
- `core/tui/file_browser.py` (`FileBrowser`) for file/directory picking
- `core/ui/selector_framework.py` and selector wrappers for reusable selection behavior
- `core/input/*` prompt handlers for typed input and fallback behavior

### 5. Command handler output contract

Terminal-facing commands should return:

- `status`
- `message`
- `output` (human-readable text block)
- optional structured fields for downstream tooling

## Required Behavior

1. Detect TTY capability before interactive selection/input.
2. Provide non-interactive fallback path for every selector-driven command.
3. Keep text output deterministic and shell-safe.
4. Treat ANSI as opt-in presentation, not semantic data.
5. Avoid coupling terminal behavior to Wizard dashboard component styles.

## Implementation Notes

- Use selector readiness guidance: `docs/howto/UCODE-SELECTOR-READINESS.md`.
- Keep command examples aligned with: `docs/howto/UCODE-COMMAND-REFERENCE.md`.
- Preserve dispatch model boundaries from `vibe`/MCP integration docs.

## Follow-up

- Audit command handlers that still assume interactive-only selection.
- Add/expand tests for TTY vs non-TTY fallback behavior.
- Ensure docs/examples use text-operation language, not GUI component language.
