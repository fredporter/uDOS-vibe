# Spatial Z-Layer, TOYBOX, and Message Theming

Version: v1.4.4+
Last Updated: 2026-02-22

This page documents the spatial z-layer system (gameplay elevation/depth), TOYBOX profile selection, and message theme switching.

**Important**: "Z-Layer" refers to **spatial/vertical coordinates in gameplay** (z-axis, elevation, depth), NOT UI rendering layers or TUI styling.

## Scope

- **Spatial data**: Z-axis coordinates for map elevation/depth
- **Message theming**: Terminal output vocabulary (not GUI styling)
- **Gameplay profiles**: TOYBOX container selection
- **All contexts**: Works in Vibe CLI, shell, and Python API

## Controls

Gameplay profile:

```bash
# Via Vibe CLI
vibe
# User: "set toybox to hethack"
# or: "switch to elite gameplay"

# Via shell
ucode GAMEPLAY TOYBOX SET hethack
ucode GAMEPLAY TOYBOX SET elite
```

Message theme (terminal output):

```bash
export UDOS_MAP_LEVEL=dungeon|foundation|galaxy
export UDOS_MESSAGE_THEME=<theme>
```

**Note**: Former `UDOS_TUI_*` variables renamed. These control message formatting, not UI rendering. Standalone ucode TUI is deprecated; Vibe CLI is exclusive interactive interface.

## Z-Layer Model (Spatial Coordinates)

**Z-layer = vertical axis in gameplay**, not UI rendering.

Spatial data includes:
- `LocId` with `-Zz` suffix (e.g., `L001-CC01-Z2` = cell 01, elevation 2)
- Per-location seed fields: `z`, `z_min`, `z_max`
- Traversal: `stairs`, `ramps`, `portals`

Recommended map-level hint mapping:

| Spatial context | `UDOS_MAP_LEVEL` | Z-range |
| --- | --- | --- |
| Underground, dungeons, negative z | `dungeon` | z < 0 |
| Surface/regional, baseline elevation | `foundation` | z ≈ 0 |
| Orbital/stellar, high-band maps | `galaxy` | z >> 0 |

## TOYBOX Lens Recipes

```bash
# Dungeon lens (underground, negative z)
vibe
# User: "set toybox to hethack with dungeon theme"

# Or via shell:
ucode GAMEPLAY TOYBOX SET hethack
export UDOS_MAP_LEVEL=dungeon
export UDOS_MESSAGE_THEME=dungeon

# Galaxy lens (orbital, high z)
vibe
# User: "switch to elite with galaxy theme"

# Or via shell:
ucode GAMEPLAY TOYBOX SET elite
export UDOS_MAP_LEVEL=galaxy
export UDOS_MESSAGE_THEME=pilot
```

## Related docs

- `docs/features/THEME-LAYER-MAPPING.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/howto/SPATIAL-QUICK-REF.md`
- `docs/specs/TOYBOX-GAMEPLAY-SCAFFOLD-v1.3.md`
