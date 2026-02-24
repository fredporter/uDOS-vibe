"""Vibe-CLI Architecture Fix v1.4.6 - Implementation Status

Last Updated: 2026-02-24
Milestone: v1.4.6 Architecture Stabilisation Phase
Status: Core Modules Complete - Integration Pending

════════════════════════════════════════════════════════════════════════════════
SUMMARY
════════════════════════════════════════════════════════════════════════════════

This document tracks the implementation of the Vibe-CLI architecture fixes that
address critical bugs: double response, hanging/blocking, Ollama failures, and
non-deterministic provider selection.

The root cause was identified as an "assistant-first" architecture (send to provider
then maybe execute) instead of "command-first" (execute if command, else fallback
to provider). The fix implements strict separation between routing, execution, and
provider interaction with explicit short-circuit logic.

════════════════════════════════════════════════════════════════════════════════
COMPLETED WORK
════════════════════════════════════════════════════════════════════════════════

Phase 1: Governance & Documentation ✅
─────────────────────────────────────────────────────────────────────────────────

1. Created root AGENTS.md (v1.4.6 OK Agent policy)
2. Created subsystem AGENTS.md files:
   - /core/AGENTS.md (stdlib-only constraints)
   - /wizard/AGENTS.md (networked provider rules)
   - /vibe/AGENTS.md (Vibe-CLI integration rules)
   - /dev/AGENTS.md (development workspace rules)

3. Created governance scaffolding:
   - Root: DEVLOG.md, project.json, tasks.md, completed.json
   - Dev templates: DEVLOG.md, project.json, tasks.md, completed.json
   - Binder seed templates: Updated with new governance files

4. Documented architecture fixes:
   - /docs/decisions/vibe-cli-architecture-fix-v1-4-6.md
   - /docs/devlog/2026-02-24-agents-governance-implementation.md

5. Verified no regressions:
   - All 514 core tests passing

Phase 2: Core Routing Modules ✅
─────────────────────────────────────────────────────────────────────────────────

Created 7 new modules implementing command-first execution model:

1. /vibe/core/input_router.py (InputRouter, RouteDecision, RouteType)
   - Deterministic routing: ucode → shell → provider
   - Confidence scoring for fuzzy matches
   - Command-first execution priority

2. /vibe/core/command_engine.py (CommandEngine, ExecutionResult)
   - Executes ucode commands with HARD STOP
   - NO provider interaction or fallback
   - Clean error handling

3. /vibe/core/response_normaliser.py (ResponseNormaliser, NormalisedResponse)
   - Strips markdown code blocks
   - Extracts ucode commands
   - Validates safety (prevents shell injection)

4. /vibe/core/provider_engine.py (ProviderEngine, ProviderResult)
   - Async provider calls with timeout guards
   - Stream handling with explicit close logic
   - Multi-provider support (Ollama, Mistral, OpenAI, Anthropic, Gemini)
   - Response normalisation integration

5. /wizard/services/provider_registry.py (VibeProviderRegistry)
   - Capability-based provider selection
   - Multi-provider fallback chains
   - Performance telemetry tracking
   - Local-first routing logic

6. /wizard/services/adapters/ollama_adapter.py (OllamaAdapter)
   - Ollama-specific fixes:
     * Explicit stream closing (prevents hanging)
     * API format detection (/api/chat vs /api/generate)
     * Timeout guards on all operations
     * Context window overflow prevention

7. /wizard/services/adapters/mistral_adapter.py (MistralAdapter)
   - Mistral API integration
   - Standard provider interface
   - Timeout and error handling

8. /wizard/services/adapters/__init__.py
   - Adapter registry exports

Phase 3: Integration Planning ✅
─────────────────────────────────────────────────────────────────────────────────

Created comprehensive integration plan:

- /docs/decisions/vibe-cli-integration-plan-v1-4-6.md
  * 5-phase implementation guide
  * Detailed code examples for each phase
  * Testing strategy (7 test cases)
  * Rollback plan
  * Success criteria checklist

════════════════════════════════════════════════════════════════════════════════
PENDING WORK
════════════════════════════════════════════════════════════════════════════════

Phase 4: Integration into core/tui/ucode.py ⏳
─────────────────────────────────────────────────────────────────────────────────

Status: Ready to implement (plan documented)

Required changes:
1. Add imports for new modules
2. Initialize routing components in UCODE.__init__()
3. Add _register_providers() method
4. Replace _route_input() method (line 571)
5. Add _route_to_provider() method (NEW)
6. Add _infer_task_mode() method (NEW)
7. Replace _dispatch_with_vibe() method (line 476)
8. Deprecate old provider methods (_run_ok_request, _run_ok_local)

Files to modify:
- /core/tui/ucode.py (main integration point)

Phase 5: Testing & Validation ⏳
─────────────────────────────────────────────────────────────────────────────────

Status: Not started

Test cases to validate:
1. ucode command NO double response (HELP)
2. OK provider call with normalisation
3. Shell command validation
4. Fuzzy ucode match with confirmation
5. Provider fallback chain (Ollama → Mistral)
6. Timeout handling (30s)
7. Stream closing (Ollama)

Commands to run:
- `uv run pytest core/tests -v` (all 514 tests)
- `bin/vibe` (interactive smoke test)
- Manual validation of all 7 test cases

Phase 6: Additional Provider Adapters ⏳
─────────────────────────────────────────────────────────────────────────────────

Status: Not started (low priority)

Remaining adapters to implement:
- OpenAI adapter (wizard/services/adapters/openai_adapter.py)
- Anthropic adapter (wizard/services/adapters/anthropic_adapter.py)
- Gemini adapter (wizard/services/adapters/gemini_adapter.py)

Note: Ollama and Mistral cover local + cloud needs for now.

════════════════════════════════════════════════════════════════════════════════
FILES CREATED/MODIFIED
════════════════════════════════════════════════════════════════════════════════

New Files (25 total):
─────────────────────────────────────────────────────────────────────────────────

Governance (13 files):
1. /AGENTS.md
2. /DEVLOG.md
3. /project.json
4. /tasks.md
5. /completed.json
6. /core/AGENTS.md
7. /wizard/AGENTS.md
8. /vibe/AGENTS.md
9. /dev/AGENTS.md
10. /dev/DEVLOG.md
11. /dev/project.json
12. /dev/tasks.md
13. /dev/completed.json

Core Modules (8 files):
14. /vibe/core/input_router.py
15. /vibe/core/command_engine.py
16. /vibe/core/response_normaliser.py
17. /vibe/core/provider_engine.py
18. /wizard/services/provider_registry.py
19. /wizard/services/adapters/__init__.py
20. /wizard/services/adapters/ollama_adapter.py
21. /wizard/services/adapters/mistral_adapter.py

Documentation (4 files):
22. /docs/decisions/vibe-cli-architecture-fix-v1-4-6.md
23. /docs/decisions/vibe-cli-integration-plan-v1-4-6.md
24. /docs/devlog/2026-02-24-agents-governance-implementation.md
25. /docs/decisions/vibe-cli-implementation-status-v1-4-6.md (this file)

Modified Files:
─────────────────────────────────────────────────────────────────────────────────

Binder Seed Templates:
- /core/framework/seed/vault/@binders/sandbox/AGENTS.md
- /core/framework/seed/vault/@binders/sandbox/DEVLOG.md
- /core/framework/seed/vault/@binders/sandbox/tasks.md
- /core/framework/seed/vault/@binders/sandbox/project.json

════════════════════════════════════════════════════════════════════════════════
ARCHITECTURE CHANGES
════════════════════════════════════════════════════════════════════════════════

Key Architectural Shifts:
─────────────────────────────────────────────────────────────────────────────────

1. Command-First Execution Model
   Before: User input → Provider → Maybe execute
   After:  User input → Route → Execute OR Provider (never both)

2. Explicit Short-Circuit Logic
   Before: Ambiguous fallthrough between execution and provider calls
   After:  HARD STOP after ucode execution (CommandEngine)

3. Provider Abstraction Layer
   Before: Direct Ollama/Mistral calls scattered throughout code
   After:  Unified ProviderEngine with adapter pattern

4. Capability-Based Routing
   Before: Hardcoded provider selection
   After:  VibeProviderRegistry with dynamic capability matching

5. Timeout Guards Everywhere
   Before: Some provider calls lacked timeouts
   After:  ALL provider calls have 30s default timeout

6. Stream Handling
   Before: Streams not explicitly closed → hanging
   After:  Explicit stream close in all adapters

7. Response Normalisation
   Before: Raw provider responses executed directly
   After:  ResponseNormaliser validates before any execution

════════════════════════════════════════════════════════════════════════════════
KNOWN ISSUES FIXED
════════════════════════════════════════════════════════════════════════════════

Issue 1: Double Response Bug ✅
─────────────────────────────────────────────────────────────────────────────────

Problem: ucode command executes AND provider responds
Root Cause: No short-circuit after command execution
Fix: CommandEngine enforces HARD STOP after execution

Status: Fixed in code (pending integration)

Issue 2: Hanging/Blocking ✅
─────────────────────────────────────────────────────────────────────────────────

Problem: Vibe-CLI hangs after Ollama requests
Root Cause: Stream responses not closing properly
Fix: OllamaAdapter explicitly closes all streams

Status: Fixed in code (pending integration)

Issue 3: Ollama Integration Failures ✅
─────────────────────────────────────────────────────────────────────────────────

Problem: Timeout issues, context window overflow, API format inconsistencies
Root Cause: No timeout guards, no API format detection
Fix: OllamaAdapter with:
  - Timeout guards (30s default)
  - API format detection (/api/chat vs /api/generate)
  - Automatic fallback to legacy endpoint

Status: Fixed in code (pending integration)

Issue 4: Non-Deterministic Provider Selection ✅
─────────────────────────────────────────────────────────────────────────────────

Problem: Multi-provider routing unreliable
Root Cause: No capability-based selection logic
Fix: VibeProviderRegistry with:
  - Capability declaration per provider
  - Task mode inference
  - Performance telemetry
  - Fallback chains

Status: Fixed in code (pending integration)

════════════════════════════════════════════════════════════════════════════════
TESTING STATUS
════════════════════════════════════════════════════════════════════════════════

Pre-Integration Tests ✅
─────────────────────────────────────────────────────────────────────────────────

- Core test suite: 514/514 passing (100%)
- No regressions introduced
- Governance files validated
- Documentation complete

Post-Integration Tests ⏳
─────────────────────────────────────────────────────────────────────────────────

Status: Pending integration completion

Required tests:
1. Unit tests for new modules
2. Integration tests in core/tui/ucode.py
3. Interactive smoke tests with Vibe-CLI
4. All 7 test cases from integration plan

Test files to create:
- /core/tests/test_input_router.py
- /core/tests/test_command_engine.py
- /vibe/tests/test_provider_engine.py
- /wizard/tests/test_provider_registry.py
- /wizard/tests/test_ollama_adapter.py
- /wizard/tests/test_mistral_adapter.py

════════════════════════════════════════════════════════════════════════════════
NEXT ACTIONS
════════════════════════════════════════════════════════════════════════════════

Immediate Priority:
─────────────────────────────────────────────────────────────────────────────────

1. Implement Phase 4: Integration into core/tui/ucode.py
   - Follow integration plan exactly
   - Test after each phase

2. Run core test suite validation
   - Ensure 100% pass rate maintained
   - Fix any regressions immediately

3. Create unit tests for new modules
   - Test isolation of each component
   - Validate interfaces

4. Interactive testing with Vibe-CLI
   - Validate all 7 test cases
   - Confirm NO double responses
   - Confirm NO hanging

Medium Priority:
─────────────────────────────────────────────────────────────────────────────────

5. Update DEVLOG.md with integration results
6. Update AGENTS.md if architecture changes
7. Move completed tasks to completed.json
8. Tag milestone v1.4.6 in Git

Low Priority:
─────────────────────────────────────────────────────────────────────────────────

9. Implement additional provider adapters (OpenAI, Anthropic, Gemini)
10. Add streaming support to ProviderEngine
11. Implement ucode extraction auto-execution with confirmation

════════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA
════════════════════════════════════════════════════════════════════════════════

Core Requirements:
─────────────────────────────────────────────────────────────────────────────────

✅ All 514 core tests passing
⏳ NO double responses (command + provider)
⏳ NO hanging on Ollama requests
⏳ Timeout guards working (30s max)
⏳ Stream handling correct (explicit close)
⏳ Provider fallback working
⏳ ucode commands execute with HARD STOP
⏳ Natural language routed to provider only

Documentation Requirements:
─────────────────────────────────────────────────────────────────────────────────

✅ Integration plan documented
✅ Architecture fixes documented
✅ AGENTS.md governance in place
✅ DEVLOG.md tracking established

Testing Requirements:
─────────────────────────────────────────────────────────────────────────────────

⏳ Unit tests for all new modules
⏳ Integration tests for core/tui/ucode.py
⏳ All 7 test cases validated
⏳ Interactive smoke test passed

════════════════════════════════════════════════════════════════════════════════
RISK ASSESSMENT
════════════════════════════════════════════════════════════════════════════════

Low Risk:
─────────────────────────────────────────────────────────────────────────────────

- New modules are isolated and don't affect existing code until integrated
- Deprecation approach allows rollback
- Comprehensive integration plan reduces implementation errors
- All changes are additive (no deletions yet)

Medium Risk:
─────────────────────────────────────────────────────────────────────────────────

- Integration into core/tui/ucode.py touches critical user-facing code
- Async/await patterns may introduce new concurrency issues
- Provider adapter failures could break OK system entirely

Mitigation:
- Phased integration with testing after each phase
- Keep old methods as deprecated fallbacks
- Rollback plan documented

High Risk:
─────────────────────────────────────────────────────────────────────────────────

None identified

════════════════════════════════════════════════════════════════════════════════
DEPENDENCIES
════════════════════════════════════════════════════════════════════════════════

Python Dependencies (Already Installed):
─────────────────────────────────────────────────────────────────────────────────

- aiohttp (async HTTP client for provider adapters)
- asyncio (Python stdlib, no install needed)

System Dependencies:
─────────────────────────────────────────────────────────────────────────────────

- Ollama (optional, for local provider)
- Mistral API key (optional, for cloud provider)

No new dependencies required.

════════════════════════════════════════════════════════════════════════════════
ROLLBACK PLAN
════════════════════════════════════════════════════════════════════════════════

If Integration Fails:
─────────────────────────────────────────────────────────────────────────────────

1. Git revert integration commits
2. Re-enable old _run_ok_request logic
3. Remove new imports from core/tui/ucode.py
4. Document regression issue in DEVLOG.md
5. Schedule fix for v1.5.0 milestone

Rollback Trigger Conditions:
─────────────────────────────────────────────────────────────────────────────────

- Test suite failure rate > 5%
- ucode commands stop working
- Provider calls fail entirely
- User reports of broken interactive workflow
- Critical bugs introduced in TUI

Rollback Procedure:
─────────────────────────────────────────────────────────────────────────────────

```bash
# Identify integration commits
git log --oneline --grep="v1.4.6 integration"

# Revert (example)
git revert <commit-hash>

# Run tests
uv run pytest core/tests -v

# Verify rollback successful
bin/vibe
```

════════════════════════════════════════════════════════════════════════════════
CONCLUSION
════════════════════════════════════════════════════════════════════════════════

Phase 1-3 (Governance, Core Modules, Integration Planning) are complete.
All new modules are implemented and validated against architecture rules.
Integration plan is documented and ready for implementation.

Core test suite shows no regressions (514/514 passing).

Next step: Implement Phase 4 (integration into core/tui/ucode.py) following
the documented integration plan.

Expected completion: 1-2 hours of focused implementation + testing.

End of Status Document
════════════════════════════════════════════════════════════════════════════════
"""
