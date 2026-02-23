# Empire Pilot Run-Sheet Template

Pilot metadata
- Date:
- Pilot org:
- Operator:
- Observer:
- Build/tag:

Pre-flight
- [ ] `scripts/smoke/phase5_launch_gate.sh` passed
- [ ] Credentials verified (HubSpot, Gmail, Places)
- [ ] Latest DB backup path recorded

Pilot limits
- HubSpot: `--limit` / `--pages`
- Gmail: `--max` / query scope
- Places: query + radius

Execution timeline
1. Start API and confirm auth health.
2. Run limited HubSpot sync.
3. Run limited Gmail sync.
4. Run limited Places sync.
5. Validate DB counters and event stream.
6. Validate UI read paths.

Validation checks
- [ ] No P0/P1 issues
- [ ] Expected records/events growth only
- [ ] No repeated integration failures
- [ ] Latency within Phase 4 budget

Rollback readiness
- [ ] Restore command verified
- [ ] Rollback owner assigned

Outcome
- Decision: GO / HOLD / ROLLBACK
- Notes:
- Follow-up actions:
