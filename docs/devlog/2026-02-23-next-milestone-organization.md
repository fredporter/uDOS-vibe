# 2026-02-23 Next Milestone Organization (v1.5-RC1)

## Purpose

Reorganize the active roadmap into one executable milestone plan with explicit ordering, exit criteria, and a short iteration queue.

## Changes

- Updated `docs/roadmap.md` with a new active section:
  - `Next Milestone: v1.5-RC1 Stabilization (Active)`
- Added milestone-level exit criteria to define done-state for RC1.
- Added ordered execution phases to make dependency order explicit.
- Added a 7-item iteration queue for the 2026-02-23 to 2026-03-06 window.
- Marked non-RC1 lanes as explicitly deferred so they do not block release readiness.

## Why

The prior roadmap was comprehensive but lacked a single, time-bounded milestone control section. This update makes the next delivery target operational: clear completion criteria, explicit sequencing, and immediate work packets.

## Next Review Checkpoint

- Re-evaluate milestone status after I3 (provider schema + fallback policy) and update checklist states in `docs/roadmap.md`.

## Follow-up Update: Milestone Closure + Next Activation

Added explicit operational sections in `docs/roadmap.md`:

- `RC1 Completion Protocol (How We Close Current Milestone)`
- `Next Milestone (Immediately After RC1): v1.5-GA Hardening`

This converts roadmap intent into a closeout procedure (validation commands, evidence expectations, close condition) and a ready-to-start GA queue so transition overhead is minimized.
