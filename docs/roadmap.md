# uDOS Roadmap (Canonical)

Last updated: 2026-02-24

This roadmap tracks active execution and planned development.

## Scope Notes

- macOS Swift thin UI source is not part of this repository and is maintained as an independent commercial companion application.
- Alpine-core thin UI remained conceptual and was not developed as an active implementation lane in this repository.
- Sonic work is tracked as a dedicated pending-round stream and must be completed before uDOS v1.5 milestone closure.

Previous roadmap snapshot is archived at:
- `/.compost/2026-02-22/archive/docs/roadmap-pre-cycle-d-2026-02-22.md`

---

## v1.4.6 Development Release (Upcoming)

**Primary Focus:** Environment configuration consolidation, testing phase verification, config alignment

### Completed Features
- ✅ Centralized `UnifiedConfigLoader` for all config sources (.env → TOML → JSON)
- ✅ Centralized `AIProviderHandler` for Ollama/Mistral status checking
- ⚠️ Centralized `PermissionHandler` created but requires bugfix (class definition)
- ⏳ Partial TUI migration to config loader (7 os.getenv() → get_config())
- ⏳ Wizard provider routes migrated to AIProviderHandler

### Planned Features
- Complete config loader migration (100+ remaining `os.getenv()` calls)
- Path constants handler (`core/services/paths.py`)
- Fix PermissionHandler class definition
- Unit tests for all 3 central handlers (0% coverage currently)
- Documentation: ENV-STRUCTURE spec completion

### Exit Criteria
- [x] Config loader implementation complete with type-safe accessors
- [ ] **FIX:** PermissionHandler class definition (critical bug)
- [ ] **CREATE:** Unit tests for 3 central handlers (test_permission_handler.py, test_ai_provider_handler.py, test_unified_config_loader.py)
- [ ] All TUI config centralized (no duplicate `os.getenv()` calls across files) - **30% complete**
- [ ] All Wizard config centralized - **10% complete**
- [ ] Path constants handler created (core/services/paths.py)
- [ ] User data paths aligned (API routes + user_service use same location)
- [ ] Secrets location documented with path constants
- [ ] Profile matrix tests pass with new config structure
- [ ] Devlog: v1.4.6 completion summary with evidence

---

## v1.4.7 Development Release (Upcoming)

**Primary Focus:** Remaining v1.5 blockers, stability improvements, final pre-release polish

### Planned Features
- Wizard config/secret sync completion and drift-repair hardening
- Sonic schema parity finalization (SQL/JSON/Python alignment)
- Cloud provider expansion (OpenRouter, OpenAI, Anthropic, Gemini)
- Ollama offline model baseline finalization
- Home Assistant integration bridge routes
- Sonic uHOME standalone packaging contract

### Exit Criteria
- [ ] Wizard secret store sync contract fully implemented
- [ ] Sonic schema drift eliminated across all layers
- [ ] Cloud provider fallback chain deterministic and tested
- [ ] Ollama tier-aware pulling stabilized
- [ ] uHOME HA bridge routes live with integration tests
- [ ] Extended integration test coverage across all new features
- [ ] Devlog: v1.4.7 completion summary with evidence

---

## Flexible Development Buffer (Optional Enhancements)

**Placeholder rounds for additional development if needed** — no committed features.

If the v1.4.6 and v1.4.7 timelines accelerate, we can add:
- Additional cloud providers
- Extended Wizard dashboard consolidation
- 3DWORLD extension packaging
- Stub remediation (Git actions, plugin stubs, dataset parsing)
- Docs normalization work

Or slot this time for burn-in, stabilization, and user validation before RC phase.

---

## v1.5 Complete Tested Working Release (Target: Q2 2026)

**Primary Focus:** Release candidate hardening → General Availability

### Release Scope (All v1.4.6 + v1.4.7 Features Plus)
- Offline/online parity validation
- Capability-tier installer gates with deterministic fallback
- Full cloud provider support matrix
- Ollama baseline with self-heal diagnostics
- Wizard config/secret sync contract verified
- Sonic drift cleanup complete
- uHOME + Home Assistant bridge live
- Sonic Screwdriver uHOME standalone packaging
- Wizard networking + beacon services stabilized

### Milestone Exit Criteria
- [x] RC1 burn-in cycle: multi-day reliability run completed
- [ ] Extended integration test suite: core/wizard/full profiles passing
- [ ] GA1: Release-candidate burn-in cycle (multi-day reliability run + failure triage)
- [ ] GA2: Post-RC stabilization sweep and doc finalization
- [ ] GA3: Release readiness validation (operator runbooks tested end-to-end)
- [ ] GA4: Final security audit and dependency scan
- [ ] All freeze-blocker lanes closed and evidence captured
- [ ] Operator readiness confirmed: deployment guides, troubleshooting, recovery paths documented

### v1.5 Launch Readiness Checklist
- [ ] Documentation: Full operator runbooks for all deployment tiers
- [ ] Minimum spec verified: Linux/macOS/Windows 10+ with explicit offline paths
- [ ] Provider fallback tested under network failures, rate limits, auth errors
- [ ] Ollama baseline proven stable across tier2/tier3 hardware profiles
- [ ] Sonic Screwdriver uHOME installer tested on compatible hardware
- [ ] Wizard networking beacon services stable under degraded conditions
- [ ] Support: Known issues list with workarounds and tracking issues filed for v1.5.x patches

---

## v1.5.1+ Patch Stream (After v1.5 GA)

Will include:
- Security fixes and dependency updates
- Stability improvements from post-GA feedback
- Non-blocking feature enhancements
- Performance optimizations

---

---

## Cycle D Completion Summary

All work from Cycle D has been completed and moved into v1.4.6 and v1.4.7 milestones above.

For detailed completion evidence and status, see:
- `docs/devlog/2026-02-23-roadmap-completed-rollup.md` - Comprehensive completion summary
- `docs/devlog/2026-02-24-testing-phase-verification.md` - Testing phase validation
- `docs/devlog/2026-02-24-env-alignment-audit.md` - Configuration system audit

### Completed Cycle D Tracks
- ✅ Minimum spec parity validation
- ✅ Installer capability gates (I1, I2)
- ✅ Cloud provider schema and fallback chain (I3)
- ✅ Ollama baseline tier pulls and self-heal (I4)
- ✅ Wizard config/secret sync drift repair (I5)
- ✅ Sonic schema contract cleanup (I6)
- ✅ RC1 validation sweep (I7)
- ✅ GA1: Release-candidate burn-in cycle
- ✅ GA2: uHOME + Home Assistant bridge
- ✅ GA3: Sonic uHOME packaging

All evidence captured in devlog/ directory.

---

## Quality Gate Rules

- [ ] Runtime logs remain under memory/logs and test artifacts remain under .artifacts paths.
- [ ] All v1.4.6 and v1.4.7 development work captured with evidence in `docs/devlog/`
- [ ] v1.5 release readiness validated through full test matrix before GA
- [ ] Known issues and patch assignments prepared for v1.5.1+ stream before launch
