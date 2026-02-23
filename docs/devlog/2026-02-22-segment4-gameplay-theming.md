# Segment 4 Complete: Gameplay + Theming Bridge (2026-02-22)

## Scope

Completed Segment 4 roadmap items:
- shared LENS/SKIN progression-variable contract + mapping docs
- non-blocking SKIN policy drift hints tied to progression/lens state
- retheme marker noise cleanup and remap matrix update

## Implementation

### Shared progression contract service

Added:
- `core/services/progression_contract_service.py`

Provides:
- canonical progression normalization (`xp`, `hp`, `gold`, `level`, `achievement_level`, metrics)
- unlock token requirement labeling
- lens readiness mapping (`hethack|elite|rpgbbs|crawler3d` via option IDs)
- recommendation text for blocked readiness
- shared skin policy context builder (`skin_lens_mismatch`, `skin_lens_unmapped`, `skin_lens_progression_drift`)

### Command surface integration

Updated:
- `core/commands/gameplay_handler.py`
  - `PLAY LENS STATUS` now includes progression-aware readiness and recommendation output
  - compact status includes readiness and next-step hints

- `core/commands/skin_handler.py`
  - `SKIN` policy context now uses shared progression contract
  - emits non-blocking progression drift flag when lens progression is blocked

- `core/commands/mode_handler.py`
  - mode fit context now uses shared skin/lens progression policy builder

### Rethme/high-noise cleanup

Updated:
- `core/tui/output.py`

Changes:
- default info-level retheme tagging now limited to configurable prefixes (`error:,warn:,warning:`)
- no default tagging for high-noise info prefixes such as `Tip:` and `Health:`
- warn/error tagging remains on by default
- added env override: `UDOS_RETHEME_INFO_PREFIXES`

## Tests Added/Updated

Added:
- `core/tests/progression_contract_service_test.py`
- `core/tests/output_retheme_tagging_test.py`

Updated:
- `core/tests/skin_progression_policy_test.py`
- `core/tests/gameplay_service_test.py`

## Validation

Command:

```bash
uv run pytest core/tests/ucode_min_spec_command_test.py core/tests/v1_4_4_command_dispatch_chain_test.py core/tests/progression_contract_service_test.py core/tests/output_retheme_tagging_test.py core/tests/skin_progression_policy_test.py core/tests/gameplay_progression_snapshot_test.py core/tests/mode_handler_test.py core/tests/gameplay_service_test.py -q
```

Result:
- `84 passed, 0 failed`

## Docs Updated

- `docs/specs/GAMEPLAY-LENS-SKIN-PROGRESSION-v1.4.8.md`
  - now documents concrete mapping tables and implementation references
- `docs/specs/TUI-ERROR-TEXT-REMAP-v1.4.7.md`
  - updated qualification rules and operator controls
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
  - added `PLAY LENS` readiness and SKIN `policy_flag` notes
- `docs/roadmap.md`
  - Segment 4 + related Cycle A/Cycle B checklist items marked complete

