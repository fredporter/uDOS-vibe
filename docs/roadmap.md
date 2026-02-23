# uDOS Roadmap (Canonical)

Last updated: 2026-02-23

This roadmap tracks active execution only.

## Scope Notes

- macOS Swift thin UI source is not part of this repository and is maintained as an independent commercial companion application.
- Alpine-core thin UI remained conceptual and was not developed as an active implementation lane in this repository.
- Sonic work is tracked as a dedicated pending-round stream and must be completed before uDOS v1.5 milestone closure.

Previous roadmap snapshot is archived at:
- `/.compost/2026-02-22/archive/docs/roadmap-pre-cycle-d-2026-02-22.md`

---

## Next Milestone: v1.5-RC1 Stabilization (Active)

Target window: 2026-03-06

### Milestone Exit Criteria

- [x] Offline/online parity is verified for minimum spec path (startup messaging, fallback order, local docs/demo coverage).
- [x] Capability-tier installer gates are enforced with deterministic provider fallback behavior.
- [x] Cloud provider contract + fallback chain is implemented and covered by integration tests.
- [x] Ollama baseline is stable for supported tiers with explicit fallback diagnostics.
- [x] Wizard config/secret sync contract is drift-safe and recovery-tested.
- [x] Sonic pending-round contract cleanup is no longer blocking v1.5 freeze.
- [x] Full profile test lanes pass through uv profile matrix with plugin-autoload disabled.

### Ordered Execution Plan

1. Platform Reliability Gates (must land first)
   - Minimum spec parity + capability tiers/install hardlines.
2. Provider Reliability (depends on platform gates)
   - Cloud provider expansion + Ollama baseline stabilization.
3. Control Plane Integrity (parallel with provider reliability)
   - Wizard config + secret store sync contract.
4. Freeze Blocker Cleanup (must close before RC1)
   - Sonic dedicated drift/contract cleanup.
5. RC1 Readiness Validation
   - Profile-matrix test runs + docs/how-to consistency pass + release checklist refresh.

### Iteration Queue (2026-02-23 to 2026-03-06)

- [x] I1: Minimum spec parity validation pass and test refresh.
- [x] I2: Installer capability probes + hardline gate enforcement.
- [x] I3: Provider schema and fallback policy implementation + tests.
- [x] I4: Ollama baseline tier pulls and health/self-heal checks.
- [x] I5: Wizard config/secret-store drift repair and lifecycle tests.
- [x] I6: Sonic schema/adapter cleanup and alias retirement checks.
- [x] I7: RC1 validation sweep and roadmap checkpoint update.

### Current Iteration (I6) Start

- Status (2026-02-23): I6 started; legacy Sonic alias retirement mode and explicit alias-status contract added as first freeze-blocker cleanup slice (`docs/devlog/2026-02-23-i6-sonic-alias-retirement-kickoff.md`).
- Status (2026-02-23): Sonic SQL/JSON/Python schema-contract parity guard landed with live dataset drift fix (`year` now required in SQL) and route-level contract endpoint (`docs/devlog/2026-02-23-i6-sonic-schema-contract-parity-slice2.md`).
- Status (2026-02-23): adapter payload invariants are now part of the Sonic contract check (SQL-column completeness + legacy usb_boot normalization) (`docs/devlog/2026-02-23-i6-sonic-adapter-contract-slice3.md`).
- Status (2026-02-23): I6 completed; Sonic contract cleanup + alias retirement checks consolidated (`docs/devlog/2026-02-23-i6-sonic-contract-cleanup-and-alias-retirement.md`).

### Current Iteration (I7) Start

- Status (2026-02-23): I7 started; RC1 validation sweep and roadmap checkpoint update in progress.
- Status (2026-02-23): I7 completed; core/wizard/full profile matrix passed with plugin autoload disabled, and profile-env mismatch + stale-module logging flake were closed (`docs/devlog/2026-02-23-i7-rc1-validation-sweep-and-roadmap-checkpoint.md`).

### Round Close (2026-02-23)

- Completed this round:
  - I1 completed with evidence: `docs/devlog/2026-02-23-i1-minimum-spec-parity-validation.md`
  - I2 completed with evidence: `docs/devlog/2026-02-23-i2-installer-capability-gates.md`
- Missed-TODO sweep (actionable, non-vendored) captured:
  - OAuth lifecycle TODOs in `core/sync/oauth_manager.py` (token exchange/refresh/revoke) -> carry into I3.
  - Sync persistence/full-sync TODOs in `core/services/vibe_sync_service.py` -> carry into I5.
  - Timezone/location default TODO in `core/tui/form_fields.py` -> carry into I5 polish pass.
  - Legacy placeholder test suites with many TODO stubs (`core/tests/v1_4_4_display_render_test.py`, `core/tests/v1_4_4_stdlib_command_integration_test.py`) -> constrain under I7 validation debt cleanup.

### Next Milestone Advancement Gate (I3 Closeout)

- [x] Define canonical provider schema object and env-key map for OpenRouter/OpenAI/Anthropic/Gemini.
- [x] Implement deterministic primary/secondary provider chain and failover classification.
- [x] Add integration tests for: missing auth, rate limit, unreachable provider, successful failover.
- [x] Add operator-facing diagnostics for failover events and no-provider terminal failure.
- [x] Record I3 evidence in `docs/devlog/` and update RC1 exit-criteria checkboxes.

### Deferred Until After RC1 (Do Not Block v1.5-RC1)

- uHOME + Home Assistant delivery lane implementation.
- Sonic Screwdriver standalone uHOME packaging/installer lane.
- 3DWORLD extension packaging lane.
- Large docs taxonomy promotion work not required for RC1 correctness.

### RC1 Completion Protocol (How We Close Current Milestone)

- [x] Run profile-matrix validation and capture evidence in `docs/devlog/`:
  - core profile: `uv sync --group dev --extra udos`
  - wizard profile: `uv sync --group dev --extra udos-wizard`
  - full profile: `uv sync --group dev --extra udos-full`
- [x] Run pytest with explicit plugin loading and autoload disabled:
  - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -p pytest_asyncio.plugin -p pytest_timeout -p xdist.plugin -p anyio.pytest_plugin -p respx.plugin -p syrupy -p pytest_textual_snapshot`
- [ ] For each exit criterion above, attach one evidence note in `docs/devlog/` with:
  - what changed
  - tests/commands run
  - pass/fail result
  - remaining risk (if any)
- [x] Mark RC1 complete only when all exit criteria are checked and no freeze-blocker lane remains open.

### Next Milestone (Immediately After RC1): v1.5-GA Hardening

Activation condition: all RC1 exit criteria are complete.
- Status (2026-02-23): activated after RC1 completion checkpoint closeout.

Initial GA queue:
- [x] GA1: Release-candidate burn-in cycle (multi-day reliability run + failure triage).
- [x] GA2: uHOME + Home Assistant bridge implementation lane.
- [x] GA3: Sonic Screwdriver standalone uHOME packaging lane.
- [ ] GA4: Wizard networking/beacon stabilization completion.
- [ ] GA5: Docs/spec normalization for finalized v1.5 surfaces and operator runbooks.

### Current Iteration (GA1) Start

- Status (2026-02-23): GA1 started; burn-in runbook and triage checklist published (`docs/devlog/2026-02-23-ga1-rc-burn-in-runbook-and-triage-checklist.md`).
- Status (2026-02-23): GA1 completed after three consecutive green profile-matrix runs; one non-blocking P3 warning deferred with owner/rationale (`docs/devlog/2026-02-23-ga1-rc-burn-in-runbook-and-triage-checklist.md`).

### Current Iteration (GA2) Start

- Status (2026-02-23): GA2 started; uHOME + Home Assistant bridge implementation lane active.
- Status (2026-02-23): Dev infrastructure stabilized — `.claude/launch.json` configured with wizard-server (port 8765, `autoPort: false`), dashboard-dev (port 5174), and web-admin-dev (port 5173); `web-admin/package.json` dev scripts migrated from `svelte-kit dev` to `vite dev` for SvelteKit 1.x compatibility.
- Status (2026-02-23): GA2 completed; Wizard HA bridge routes (status/discover/command) + HA service contract + FastAPI integration tests landed (`docs/devlog/2026-02-23-ga2-uhome-ha-bridge-routes.md`).

### Current Iteration (GA3) Start

- Status (2026-02-23): GA3 started; Sonic Screwdriver standalone uHOME packaging lane active.
- Status (2026-02-23): GA3 completed; uHOME hardware preflight checker, bundle artifact contract (manifest/checksums/rollback), and install plan builder landed with 21-test suite (`docs/devlog/2026-02-23-ga3-sonic-uhome-packaging.md`).

---

## Cycle D

- Completed items and evidence were moved to:
  - `docs/devlog/2026-02-23-roadmap-completed-rollup.md`

### Pre-v1.5 Stable: Minimum Spec (vibe-cli + uCode Addon) Online/Offline Parity
- Status (2026-02-23): milestone-level parity gate completed via I1; see `docs/devlog/2026-02-23-i1-minimum-spec-parity-validation.md`.
- [ ] Re-validate and publish minimum runtime profile: Linux/macOS/Windows 10+, 2 CPU cores, 4 GB RAM, 5 GB free storage.
- [ ] Keep both execution pathways explicitly supported in command/help surfaces:
  - networked mode: full `uCODE` command set + cloud provider routing
  - offline mode: local demos/docs/system introspection only
- [ ] Confirm offline fallback routing order remains deterministic:
  - demos (`UCODE DEMO LIST`/`UCODE DEMO RUN`)
  - docs lookup (`UCODE DOCS`)
  - system introspection (`UCODE SYSTEM INFO`/`UCODE CAPABILITIES`)
- [ ] Add/refresh first-run offline guidance text in launcher/setup flows when network is unavailable.
- [ ] Standardize naming and aliases in docs/help text:
  - `ucli` references map to canonical `uCODE` commands (and alias behavior is documented)
  - avoid drift between README/howto/spec examples
- [ ] Define one canonical local data path contract for offline assets (demos/docs/cache) and document migration from legacy paths.
- [ ] Add/refresh integration tests for offline mode covering:
  - no-network startup messaging
  - fallback order behavior
  - local docs + demo command availability

### Pre-v1.5 Stable: Capability Tiers + Install Hardlines (vibe-cli/Ollama)
- Status (2026-02-23): capability preflight + hardline gate baseline completed via I2; see `docs/devlog/2026-02-23-i2-installer-capability-gates.md`.
- [ ] Add preflight capability detection in install/setup scripts:
  - OS/version check
  - CPU architecture + core count
  - RAM + free storage checks
  - optional GPU/VRAM probe when local-model mode is requested
- [ ] Define and document runtime tiers with deterministic selection:
  - Tier 1: `vibe-cli` + cloud fallback only (minimum hardware)
  - Tier 2: `vibe-cli` + Ollama small models + cloud fallback
  - Tier 3: `vibe-cli` + Ollama larger models + cloud fallback
- [ ] Encode hardline compatibility gates in installer and diagnostics:
  - unsupported OS/legacy platform -> block local-model path, keep cloud-only path
  - insufficient RAM/storage -> block local-model path with explicit remediation
- [ ] Add startup provider-fallback policy checks:
  - local model primary (if configured and healthy)
  - cloud provider secondary
  - explicit terminal error if no provider is available
- [ ] Add setup validation for stale/invalid commands and config drift:
  - reject deprecated commands in launch scripts (for example legacy trust flow)
  - verify MCP server path targets current repo runtime
  - verify provider config points to reachable backends
- [ ] Add smoke tests for each tier profile:
  - tier selection correctness under simulated hardware/env inputs
  - provider fallback behavior when local backend is unavailable
  - no-hang guarantee for setup/launch flow with invalid legacy inputs

### Pre-v1.5 Stable: Cloud Provider Expansion (vibe-cli)
- Status (2026-02-23): canonical cloud-provider schema + deterministic failover chain landed in core cloud path; see `docs/devlog/2026-02-23-i3-provider-schema-and-fallback.md`.
- [ ] Expand supported cloud provider contracts beyond current defaults to include:
  - OpenRouter
  - OpenAI
  - Anthropic
  - Google Gemini/Google Cloud
- [ ] Define canonical provider schema in config/docs:
  - api base/url, auth env var, model mapping, timeout/retry policy, streaming behavior
  - per-provider feature flags (tool-calling, reasoning fields, token accounting)
- [ ] Add provider selection/fallback policy:
  - explicit primary/secondary provider chain
  - deterministic failover on provider outage/rate-limit/auth errors
  - clear terminal diagnostics when failover occurs
- [ ] Extend installer/setup guidance to provision provider env keys safely without forcing local-model setup.
- [ ] Add integration tests for provider routing and fallback:
  - auth-missing path
  - rate-limit path
  - provider-unreachable path
  - successful failover to secondary provider
- [ ] Update docs/howto and minimum-spec references so networked mode examples remain provider-agnostic while keeping concrete setup pages per provider.

### Pre-v1.5 Stable: Ollama + Offline Model Baseline (Wizard-Aligned)
- Status (2026-02-23): tier-aware Ollama pull baselines + self-heal default-model diagnostics completed via I4; see `docs/devlog/2026-02-23-i4-ollama-baseline-tier-pulls-and-self-heal.md`.
- [ ] Re-enable and stabilize Ollama-first local model pathway for supported tiers while retaining cloud fallback.
- [ ] Align installer/model bootstrap with currently configured Wizard offline model baseline:
  - router default local model: `devstral-small-2` (`wizard/services/model_router.py`)
  - catalog baseline from `wizard/services/ollama_service.py`: `mistral`, `devstral-small-2`, `llama3.2`, `qwen3`, `codellama`, `phi3`, `gemma2`, `deepseek-coder`
- [ ] Add tier-aware default pull profiles:
  - tier2: smaller/fast local defaults
  - tier3: expanded local catalog + optional heavier pulls
- [ ] Ensure runtime provider order is explicit and testable:
  - local/Ollama primary when healthy
  - cloud provider fallback when local is unavailable or disabled
  - clear user-facing diagnostics for fallback reason
- [ ] Add health checks and self-heal hooks for local model readiness:
  - Ollama reachability
  - installed model presence vs configured default
  - actionable remediation prompts from Wizard UI/API

### Pre-v1.5 Stable: Wizard Config + Secret Store Sync Contract
- Status (2026-02-23): admin token/key/config/secret-store contract drift checks + repair endpoints and lifecycle coverage completed via I5; see `docs/devlog/2026-02-23-i5-wizard-config-secret-contract-drift-repair.md` and `docs/howto/WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md`.
- [ ] Synchronize Wizard Config page state with `.env`, `wizard/config/wizard.json`, and secret store as one contract (no drift between views).
- [ ] Enforce admin token/key coherence:
  - `.env` `WIZARD_ADMIN_TOKEN` and `WIZARD_KEY`
  - `wizard/config/wizard.json` `admin_api_key_id`
  - secret store entry `wizard-admin-token`
- [ ] Add startup drift checks with explicit repair actions when any of the above are mismatched or missing.
- [ ] Add integration tests for config sync lifecycle:
  - rotate token from Config page and persist to `.env` + secret store
  - reboot/restart and verify token/key still unlock routes
  - recover from tomb/key mismatch using repair endpoint without manual file edits
- [ ] Add an operator how-to covering safe token rotation, secret-store repair, and post-rotation verification commands.

### Pre-v1.5 Stable: Wizard Dashboard (Svelte) Consolidation + Function Verification
- [ ] Consolidate overlapping/legacy Svelte pages under `wizard/dashboard/src/routes/` into a reduced canonical set (remove duplicate role pages and deprecated v1.x variants after parity checks).
- [ ] Produce a user-confirmed legacy removal list for Wizard server surfaces (routes/services/web/dashboard/docs) before any delete/compost action.
- [ ] Define route ownership and API contract map for each retained page (`Config`, `Setup`, `Workflow`, `Tasks`, `Logs`, `Library`, etc.) and mark unsupported pages for compost.
- [ ] Add smoke coverage for retained routes against current Wizard API endpoints (page load, fetch success/failure states, auth-token handling).
- [ ] Add regression checks for any updated page functions before release:
  - config save/import/export
  - secret store sync/unlock/repair flows
  - task/workflow scheduler controls
  - logs/events streaming surfaces
- [ ] Ensure dashboard build remains green after consolidation and route cleanup.

### Pre-v1.5 Stable: uHOME + Home Assistant Integration
- [ ] Integrate `docs/decisions/uHOME-spec.md` into active product planning with a concrete v1.5 delivery lane.
- [ ] Upgrade `docs/decisions/HOME-ASSISTANT-BRIDGE.md` from draft-stub to a v1.5-ready bridge contract.
- [ ] Implement Wizard Home Assistant bridge routes for uHOME controller UX:
  - GET `/api/ha/status`
  - GET `/api/ha/discover`
  - POST `/api/ha/command`
- [ ] Add uHOME game-controller UX flow:
  - tuner/source discovery
  - DVR rule controls (schedule/rule-based)
  - ad-processing mode controls (skip markers vs hard cut)
  - playback handoff targets (LAN client/TV profile)
- [ ] Add integration tests for uHOME + HA bridge under FastAPI/Wizard profile (route auth, discovery payload shape, safe command execution).

### Pre-v1.5 Stable: Sonic Screwdriver uHOME Packaging + Installer
- [ ] Define Sonic Screwdriver as the canonical packager/installer path for uHOME deployments on compatible hardware.
- [ ] Add standalone install flow where Sonic can install a working uHOME application without requiring a preinstalled uDOS environment.
- [ ] Define hardware compatibility profile and preflight checks for standalone uHOME installs (CPU/RAM/storage/network/tuner requirements).
- [ ] Add artifact contract for uHOME install bundles produced by Sonic (manifest, checksums, version pinning, rollback metadata).
- [ ] Add install verification tests for Sonic-produced uHOME bundles (fresh device install, idempotent rerun, rollback-on-failure).
- [ ] Ensure post-install UX boots directly into uHOME controller mode with clear recovery path.

### Pre-v1.5 Stable: Wizard Networking + Beacon Stabilization
- [ ] Revive and stabilize Wizard Beacon services for home networking scenarios (`wizard/services/beacon_service.py` + beacon routes/tests).
- [ ] Define and enforce a small-packet transport contract for home-control and sync messages (size bounds, retry rules, ack semantics).
- [ ] Integrate MeshCore transport service paths from `extensions/transport/meshcore/` into the Wizard networking lane with deterministic fallbacks.
- [ ] Promote extension-drafted transport services into validated Wizard routes/workflows (status, health, send, receive, sync hooks).
- [ ] Add FastAPI integration coverage for networking lifecycle:
  - beacon config/update/status
  - device registration/auth paths
  - mesh sync transport bridge
  - failure/recovery behavior under partial network conditions
- [ ] Add uHOME controller networking checks:
  - LAN discovery reliability
  - low-latency control packet handling
  - safe degraded mode when transport backend is unavailable

### Pre-v1.5 Critical Juncture: Duplicate/Drift Refactor Track
- Completed items moved to:
  - `docs/devlog/2026-02-23-roadmap-completed-rollup.md`
- [ ] Collapse utility sprawl (path/fs/json/log/time/hash helpers) into canonical modules and remove redundant wrappers.
  - Status: canonical `core/services/path_service.py` added and now backs `core/services/logging_api.py` + `wizard/services/path_utils.py` repo-root resolution.
  - Status: editor workspace-path resolution is centralized in `core/services/editor_utils.py` and consumed by `wizard/services/editor_utils.py`.
  - Status (2026-02-23): added canonical helpers `core/services/json_utils.py`, `core/services/hash_utils.py`, and `core/services/time_utils.py`; Wizard/Sonic state + manifest services now consume these shared helpers.
  - Status: broader utility family cleanup is still pending outside the migrated Wizard/Sonic surfaces.
- [ ] Standardize logging contract (levels, formatting policy, sink routing) so runtime logs converge under memory/logs policy.
  - Status: logger compatibility normalization is now centralized in `core/services/logging_api.py` (`default_component` handling), and Wizard wrapper delegates instead of maintaining duplicate alias logic.
  - Status: inline suppression was removed from `wizard/services/logging_api.py`; wrapper now imports core logging symbols directly.
  - Status: non-core stacks `distribution/plugins/api/server_modular.py` and `vibe/core/utils.py` now route through core logger contract instead of local rotating/basicConfig handlers.
  - Status: `core/input/smart_prompt.py` debug path now routes through core logging API (no ad-hoc stream handler), and `Logger.exception()` compatibility alias was added for stdlib parity.
  - Status (2026-02-23): `wizard/services/cdn_upload_handler.py` now uses Wizard/core logging contract instead of direct stdlib logger wiring.
  - Status: follow-up cleanup still pending for legacy log consumers expecting old plain-text log files.

### Pre-v1.5 Pending Round: Sonic Dedicated Drift and Contract Cleanup
- [ ] Establish one canonical Sonic schema contract (SQL + JSON schema + typed interfaces) with generated or validated parity checks.
- Completed items moved to:
  - `docs/devlog/2026-02-23-roadmap-completed-rollup.md`
- [ ] Normalize Sonic DB adapters so DB -> API/UI/runtime mapping is centralized and test-covered.
  - Status (2026-02-23): Sonic runtime state/manifest JSON adapters now use canonical core helper modules; DB mapping centralization remains open.
- [ ] Remove duplicate Sonic route aliases once contract parity is verified.
  - Status: legacy Sonic service wrapper removed; route aliases now run as explicit deprecation shims over canonical `/sync/*` endpoints.
- [ ] Complete this Sonic track before uDOS v1.5 freeze.

### Pre-v1.5 Stub Remediation Track (Audit-Driven)
- [ ] Extension service Git action stubs in `wizard/services/extension_handler.py` (pull/push/issues/pr/webhook paths).
- [ ] Plugin command migration placeholder in `wizard/routes/plugin_stub_routes.py` and related MCP stub surface in `wizard/mcp/mcp_server.py`.
- [ ] Dataset parse/export stubs in `wizard/routes/dataset_routes.py`.
- [ ] VSCode bridge execution stubs in `wizard/services/vscode_bridge.py`.
- [ ] iCloud handler stubs in `wizard/services/icloud_handler.py`.
- [ ] Web service/server placeholder paths in `wizard/web/web_service.py` and related web app stubs.
- [ ] Plugin factory build-script stub path in `wizard/services/plugin_factory.py`.

### Pre-v1.5 Docs Normalization: Features vs Specs vs How-to
- [ ] Classify and normalize priority feature docs into the correct doc type and keep links synchronized.
- [ ] Promote `docs/features/alpine-core.md` to a canonical spec in `docs/specs/` (retain short feature overview with pointer).
- [ ] Promote `docs/features/DIAGRAM-SPECS.md` to a canonical spec in `docs/specs/` (retain feature summary with pointer).
- [ ] Promote `docs/features/wizard-networking.md` to a canonical spec in `docs/specs/` and add an operator runbook in `docs/howto/`.
- [ ] Promote `docs/features/beacon-portal.md` and `docs/features/beacon-vpn-tunnel.md` into one networking/beacon spec + one practical how-to.
- [ ] Keep `docs/features/THEME-LAYER-MAPPING.md` as a feature reference; add/refresh cross-links to command/how-to docs.
- [ ] Keep `docs/features/Emoji-Support.md` as a feature reference if implementation-facing detail stays accurate; otherwise promote to spec.
- [ ] Keep `docs/features/3D-WORLD.md` as a feature-facing architecture brief and create a canonical extension contract spec in `docs/specs/` for implementation.
- [ ] Update `docs/README.md` and `docs/specs/README.md` after normalization so discovery reflects final canonical locations.

### Pre-v1.5 Stable: 3DWORLD Extension Packaging
- [ ] Package 3DWORLD as a heavy optional extension in `/extensions/3dworld/` using the same manifest/container model used by `/extensions/groovebox/`.
- [ ] Define and enforce gameplay mapping contract from canonical uDOS state to 3D runtime:
  - LENS -> camera/discovery behaviors
  - SKIN -> material/theme bindings
  - GRID LOCATION -> anchor/chunk placement
  - Z axis -> deterministic elevation/progression semantics
- [ ] Keep uDOS as source of truth; ensure 3DWORLD adapters cannot mint canonical IDs or persistence outside core contracts.
- [ ] Add phased client adapters for desktop first, then VR and uHOME-compatible game-console UX without forking gameplay semantics.
- [ ] Add extension-level tests validating deterministic mapping and safe disable/enable behavior (core gameplay remains fully functional without 3DWORLD installed).

---

## Quality Gate Rules

- Completed items moved to:
  - `docs/devlog/2026-02-23-roadmap-completed-rollup.md`
- [ ] Runtime logs remain under memory/logs and test artifacts remain under .artifacts paths.
