# Empire Roadmap

Version track
- Beta: `v0.0.1` (completed)
- Alpha: `v1.0.0` (engineering readiness package completed)

## Phase Status

Phase 1: Internal Beta Baseline
- Status: COMPLETE
- Outcomes:
  - API, ingest, normalize, and storage baseline executed.
  - Smoke runs completed (non-web path).
  - Defect triage model defined (`P0/P1/P2/P3`).

Phase 2: Alpha Stabilization
- Status: COMPLETE (non-web + API hardening)
- Outcomes:
  - API deprecation warning path fixed (`regex` -> `pattern`).
  - Repeatable API smoke scripts added.
  - Three consecutive green smoke runs achieved.

Phase 3: Integrations (No Live Data)
- Status: COMPLETE
- Outcomes:
  - Strict integration preflight added and passing (`WARN=0`, `FAIL=0`).
  - Mocked integration end-to-end smoke added and passing (HubSpot, Gmail, Places).
  - Integration setup helpers completed, including Places key setup helper.

Phase 4: Pre-Alpha Hardening
- Status: COMPLETE
- Outcomes:
  - API performance baseline and budget defined.
  - DB backup/restore sanity checks automated and passing.
  - Restore drill documented.
  - Web production build regression passing.
  - Runtime production dependency audit clean (`0` vulnerabilities).

Phase 5: Live Connect + Launch Package
- Status: COMPLETE (launch package GO)
- Outcomes:
  - Live connect playbook, monitoring checklist, operator guide, and release notes published.
  - Launch-gate script added and passing.
  - CI workflow added for launch-gate execution.
  - Pilot run-sheet template added.

## Current State

Engineering readiness
- Launch package is complete and validated in repository context.
- Quality gates, smoke tooling, CI checks, and runbooks are in place.

Remaining rollout work
- Replace placeholder/mock credentials with live production credentials during rollout window.
- Execute pilot-org live rollout using:
  - `docs/empire-live-connect-playbook.md`
  - `docs/empire-pilot-runsheet-template.md`
- Enable monitoring/alert routing in production.
- Record pilot decision (`GO/HOLD/ROLLBACK`) and expand rollout scope.

## Round Closeout

Round result
- This delivery round is CLOSED.
- Empire is launch-package complete through Phase 5, pending live pilot execution and production cutover.
