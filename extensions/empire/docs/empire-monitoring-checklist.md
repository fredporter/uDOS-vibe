# Empire Monitoring Checklist (Phase 5)

API
- [ ] `/health` check every minute
- [ ] Error rate and 5xx tracking enabled
- [ ] p95 latency alert for `/records`, `/events`, `/tasks`

Integrations
- [ ] HubSpot sync event count monitored
- [ ] Gmail fetch/process event count monitored
- [ ] Places fetch event count monitored
- [ ] Alert on repeated integration failures

Data Integrity
- [ ] Record growth trend monitored
- [ ] Unexpected duplicate surge monitored
- [ ] Event logging continuity verified

Operations
- [ ] Daily backup artifact created
- [ ] Restore drill cadence scheduled
- [ ] On-call owner and escalation path documented
