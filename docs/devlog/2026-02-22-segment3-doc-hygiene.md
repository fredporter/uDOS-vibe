# Segment 3 Complete: Runtime + Doc Hygiene (2026-02-22)

## Scope

Completed the Segment 3 roadmap slice:
- remove legacy standalone-TUI wording from active docs
- align command-contract docs/examples with current dispatcher behavior
- add cross-links from active docs to composted legacy references

## Changes

### Updated command and contract docs

- `docs/howto/UCODE-COMMAND-REFERENCE.md`
  - aligned command-surface section to current dispatch/contract source files
  - updated quick checks to current offline + dispatcher-safe commands
  - added legacy-doc compost cross-links

- `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md`
  - updated title/version to v1.3.20
  - replaced stale absolute paths with workspace-relative canonical paths

### Removed/normalized legacy runtime wording

- `docs/ARCHITECTURE.md`
  - clarified `core/tui` as command infrastructure only
  - preserved Vibe-first runtime wording
  - added compost links for legacy TUI migration references

- `docs/howto/SEED-INSTALLATION-GUIDE.md`
  - replaced `Launch-uCODE.sh`/bare python examples with `vibe` + `./bin/ucode`
  - normalized wording from "TUI" to command-interface terms in active sections

- `docs/specs/UCODE-PROMPT-SPEC.md`
  - updated scope wording to Vibe CLI/ucode command interface phrasing

### Replaced noisy historical spec body with canonical pointer

- `docs/specs/vibe-spec-v1-4.md`
  - replaced prior draft content with a concise bridge spec
  - linked canonical active docs
  - linked composted standalone-TUI materials

### Troubleshooting alignment

- `docs/troubleshooting/README.md`
  - replaced `Launch-uCODE.sh` and bare `python3`/`pip` examples with `vibe`, `./bin/ucode`, `uv run`, and `uv pip`
  - added legacy-TUI cross-links under Related Documentation

## Roadmap Updates

Updated `docs/roadmap.md`:
- Segment 3 checklist: all three items marked complete.
- Milestone 2.2 item marked complete: active-doc cross-links to composted legacy docs.

