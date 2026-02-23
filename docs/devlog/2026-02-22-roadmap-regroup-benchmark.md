# Roadmap Regroup + Benchmark Snapshot (2026-02-22)

## Scope

Round objective: continue into the next roadmap round by landing actionable Cycle B work and establishing an execution baseline for the remaining tree.

## Completed in This Round

1. `UCODE UPDATE` now performs real refresh behavior when network is available:
- Re-seeds offline demo assets.
- Re-seeds/copies canonical local docs into `~/.vibe-cli/ucode/docs`.
- Writes `~/.vibe-cli/ucode/update-manifest.json` with UTC timestamp.

2. `UCODE CAPABILITIES --filter` now supports installation profile mapping:
- `core`
- `full`
- `wizard`

3. Offline fallback-order coverage added in tests:
- Expected order: `UCODE DEMO LIST` -> `UCODE DOCS --query <text>` -> `UCODE SYSTEM INFO`.

## Benchmarks / Test Baseline

### Targeted UCODE suite

Command:

```bash
uv run pytest core/tests/ucode_min_spec_command_test.py -q
```

Result:
- 9 passed, 0 failed.

### Dispatch-chain baseline (existing regressions)

Command:

```bash
uv run pytest core/tests/v1_4_4_command_dispatch_chain_test.py -q
```

Result:
- 41 passed, 8 failed.
- Main failure clusters:
  - Stage 1 command matching ambiguity (`PLACE` matched as `PLAY`).
  - Stage 2 shell routing/validation mismatch (safe command stage expectation, injection handling).
  - Stage 3 skill inference drift (`device`/`script`/`ask` misrouted).

## Roadmap Regrouping

`docs/roadmap.md` updated with an "Achievable Segments (Regrouped 2026-02-22)" section:
- Segment 1: Offline baseline completion.
- Segment 2: Dispatch stability before expansion.
- Segment 3: Runtime/doc hygiene gates.
- Segment 4: Gameplay + theming bridge.

Cycle B checklist was updated to mark the first three deliverables complete.

## Files Changed

- `core/commands/ucode_handler.py`
- `core/tests/ucode_min_spec_command_test.py`
- `docs/roadmap.md`
- `docs/devlog/2026-02-22-roadmap-regroup-benchmark.md`

