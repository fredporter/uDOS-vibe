# Empire v1.0.0-alpha Release Notes

Date
- 2026-02-15

Summary
- Completed stabilization and hardening through Phase 5 launch package.
- Added repeatable smoke, integration preflight, backup/restore, and launch gate automation.

Key changes
- API hardening and auth-aware smoke behavior.
- Integration readiness and mocked no-live sync validation for HubSpot, Gmail, and Places.
- Backup/restore verification and restore drill documentation.
- Performance baseline and alpha gate thresholds.
- Web production build validation.

Operational additions
- `scripts/smoke/phase5_launch_gate.sh`
- `docs/empire-live-connect-playbook.md`
- `docs/empire-monitoring-checklist.md`
- `docs/empire-operator-guide.md`

Known constraints
- This phase validates launch package readiness in repository context.
- Live provider cutover uses rollout-window production credentials and pilot-org sequencing.
