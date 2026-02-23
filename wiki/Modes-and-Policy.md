# Modes and Policy

This page defines the runtime modes in uDOS and why they exist.

## Why Modes Exist

uDOS is designed to be safe on first run, educational by default, and explicit about boundaries between:
- Simulation/gameplay
- Tangible user productivity and wellness tasks
- Core/runtime development work

Modes prevent accidental destructive operations, keep UX predictable, and reduce confusion between playful flows and real operations.

## Ghost Mode

### Definition
- Default first-run mode when user identity/setup is incomplete.
- Also used as safe/recovery mode after reset/fatal-error recovery paths.

### Why
- Protects fresh installs from destructive changes before identity/API/setup is complete.
- Provides a guided demo/education path so users can explore capabilities safely.
- Keeps high-risk commands blocked or dry-run only.

### Behavior
- Read-heavy and demo-friendly commands remain available.
- Write/destructive operations are blocked or simulated.
- Exit path is explicit: run `SETUP`.

## User Mode

### Definition
- Normal daily mode (not Ghost, not Dev).

### Why
- Keeps uDOS focused on high-value local productivity/wellness workflows.
- Protects core runtime and contributor surfaces from accidental modification.
- Prevents unnecessary “full coding agent” behavior when not needed.

### Behavior
- Scripting remains centered on uCode command/script surfaces.
- Broad external technology-topic routing is constrained.
- Device/SONIC-oriented technology workflows remain available.

## Wizard Mode

### Definition
- Admin operations mode between User and Dev.

### Why
- Allows elevated packaging/distribution/runtime-admin tasks without opening core/extension contribution surfaces.
- Keeps “operator/admin” workflows separate from contributor/dev workflows.

### Behavior
- Suitable for package/distribution operations and Wizard platform controls.
- Does not grant full core/extension source contribution permissions by itself.

## Dev Mode

### Definition
- Explicit admin/contributor mode for core and extension development.
- Requires admin permissions plus active dev-mode state.

### Why
- Separates contributor responsibilities from normal user workflows.
- Keeps core/editing privileges intentional and auditable.

### Behavior
- Enables development-oriented operations on core/extension surfaces.
- Intended for code contributions and advanced maintenance.

## Toybox vs Tangible Tasks

### Toybox
- Gameplay/simulation container context.
- Preserves playful and educational interactions.

### Tangible Tasks
- Real user productivity/wellness outcomes.
- Uses uCode and operational command surfaces.

### Why this split matters
- Avoids blending simulation outcomes with real-world operational state.
- Lets the assistant “play along” while keeping gameplay metrics isolated.

Example:
- “Fly to the moon and retrieve a lunar rock” should be treated as gameplay/Toybox progress, not as a real operational task.

## Policy Rollout

- Current phase: boundaries are flagged, not enforced by default.
- Enforcement is tracked as a pre-launch roadmap item.
- Use `MODE STATUS` to inspect:
  - Active mode (Ghost/User/Wizard/Dev)
  - Boundary enforcement flag
  - Active TUI theme
