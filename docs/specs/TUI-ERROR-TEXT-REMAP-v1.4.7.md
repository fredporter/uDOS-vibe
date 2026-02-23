# TUI Error Text Remap (v1.4.7)

## Scope

Define a compact remap plan for TUI text outputs so error/warn/tip language aligns with selected genre themes without losing operational clarity.

## Current Phase

- Runtime policy boundaries: **flag-only** (not enforced).
- Theme remap markers: enabled via output tags for qualifying lines.
- Marker format: `[RETHEME-CANDIDATE]`.
- High-noise cleanup applied: generic `Tip:`/`Health:` info lines are no longer tagged by default.

## Why

- Keep genre/theming visible during development.
- Avoid theme drift and seed bloat by explicitly tagging text that still uses generic lingo.
- Preserve safe operator language while expanding themed UX.

## Qualification Rules (Current)

Lines are tagged as retheme candidates when:

- Output level is `warn` or `error`, or
- Info-level text begins with configured prefixes from `UDOS_RETHEME_INFO_PREFIXES` (default: `error:,warn:,warning:`).

Default behavior intentionally excludes high-noise info prefixes such as `Tip:` and `Health:`.

## Remap Matrix (Draft)

| Base Label | Current Generic Form | Genre-Aware Target |
|---|---|---|
| Error | `ERROR:` | Theme-specific error label |
| Warning | `WARN:` / `WARNING:` | Theme-specific caution label |
| Tip | `Tip:` | Theme-specific tip label |
| Health | `Health:` | Theme-specific diagnostics label |

## Operator Controls

- `UDOS_RETHEME_TAGS=1|0` toggles candidate marker emission.
- `UDOS_RETHEME_INFO_PREFIXES="<csv>"` overrides info-level prefix tagging.
  - Example: `UDOS_RETHEME_INFO_PREFIXES=error:,warn:,warning:,tip:`

## Command Surface

- `MODE STATUS` shows active mode + policy + active theme.
- `MODE THEME ...` bridges theme commands to keep theme controls discoverable.
- `THEME ...` remains canonical for direct theme operations.

## Pre-Launch Exit Criteria

- Replace flag-only candidate tagging with stable remapped copy for high-frequency paths.
- Reduce or remove `[RETHEME-CANDIDATE]` markers from production-facing defaults.
- Enable policy enforcement toggle for mode boundaries once remap pass is complete.
