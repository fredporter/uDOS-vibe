# Wizard

Version: v1.4.4+
Last Updated: 2026-02-22

Wizard is the network-capable gateway for provider/integration/full-system operations.

## What Wizard owns

- Provider management
- Integration checks and setup
- Full Wizard-side shakedown
- AI/model access for Core clients

## Commands

```bash
WIZARD START
WIZARD STOP
WIZARD STATUS
WIZARD CHECK
WIZARD PROV LIST
WIZARD PROV STATUS
WIZARD PROV GENSECRET
WIZARD INTEG status
```

## Ownership boundary

- Core can be AI-capable through Wizard.
- Core command paths call Wizard services for model/provider access.
- Top-level core `PROVIDER` and `INTEGRATION` commands are removed in the current v1.4.3 baseline.

## Operational note

If Wizard is not running, provider/integration/model operations are unavailable even when Core is running.

## TOYBOX runtime and lens note

Wizard exposes TOYBOX runtime/container routes, while Core owns command dispatch and TUI message-layer selection.

- Runtime lens/profile examples: `hethack` (dungeon), `elite` (galaxy)
- Core command for profile selection: `GAMEPLAY TOYBOX SET ...`
- Core env for message-layer switching:
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=<theme>`

See: [TUI Z-Layer, TOYBOX, and Theme Switching](TUI-Z-Layer-and-TOYBOX.md)
