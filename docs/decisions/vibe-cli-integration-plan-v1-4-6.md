"""Integration Plan - Vibe-CLI Architecture Fix v1.4.6

This document specifies how to integrate the new routing modules into core/tui/ucode.py
to fix the double response bug, hanging issues, and Ollama failures.

Last Updated: 2026-02-24
Milestone: v1.4.6 Architecture Stabilisation Phase
Status: Ready for Implementation

════════════════════════════════════════════════════════════════════════════════
PROBLEM STATEMENT
════════════════════════════════════════════════════════════════════════════════

Current Issues:
1. Double Response Bug: Both ucode execution AND provider response happen
2. Hanging/Blocking: Stream responses not closing properly
3. Ollama Failures: Timeout issues, context window overflow, API format issues
4. Non-Deterministic Routing: Provider selection unreliable

Root Cause:
- Current architecture is "assistant-first" (sends to provider then maybe executes)
- Should be "command-first" (execute if command, else fallback to provider)
- No clear separation between routing, execution, and provider interaction
- Missing timeout guards and stream handling

════════════════════════════════════════════════════════════════════════════════
NEW MODULES CREATED
════════════════════════════════════════════════════════════════════════════════

1. /vibe/core/input_router.py
   - RouteDecision, RouteType, InputRouter
   - Deterministic routing: ucode → shell → provider
   - Priority: Command-first execution

2. /vibe/core/command_engine.py
   - CommandEngine, ExecutionResult
   - Executes ucode commands with HARD STOP
   - NO provider interaction or fallback

3. /vibe/core/response_normaliser.py
   - ResponseNormaliser, NormalisedResponse
   - Strips markdown, extracts ucode, validates safety
   - Prevents shell injection

4. /vibe/core/provider_engine.py
   - ProviderEngine, ProviderResult, ProviderType
   - Async provider calls with timeout guards
   - Stream handling with explicit close logic
   - Multi-provider support (Ollama, Mistral, OpenAI, Anthropic, Gemini)

5. /wizard/services/provider_registry.py
   - VibeProviderRegistry, ProviderCapabilities, TaskMode
   - Capability-based routing
   - Multi-provider fallback chains
   - Performance telemetry

6. /wizard/services/adapters/ollama_adapter.py
   - OllamaAdapter with stream/timeout fixes
   - API format detection (/api/chat vs /api/generate)
   - Explicit stream closing

7. /wizard/services/adapters/mistral_adapter.py
   - MistralAdapter for Mistral API integration

════════════════════════════════════════════════════════════════════════════════
INTEGRATION POINTS
════════════════════════════════════════════════════════════════════════════════

Target File: /core/tui/ucode.py

Key Methods to Modify:
1. _dispatch_with_vibe (line 476)
   - Currently handles three-stage dispatch
   - REPLACE with InputRouter-based logic

2. _route_input (line 571)
   - Currently routes based on prefix (?, OK, /)
   - INTEGRATE InputRouter for ALL routing decisions

3. _run_ok_request (line 3213)
   - Currently handles provider calls directly
   - REPLACE with ProviderEngine async calls

4. _run_ok_local (line 3121)
   - Currently calls provider directly
   - REPLACE with ProviderEngine + OllamaAdapter

════════════════════════════════════════════════════════════════════════════════
IMPLEMENTATION STEPS
════════════════════════════════════════════════════════════════════════════════

Phase 1: Add Imports and Initialize Components
─────────────────────────────────────────────────────────────────────────────────

Add imports at top of ucode.py:

```python
# New imports for v1.4.6 architecture fix
from vibe.core.input_router import InputRouter, RouteType
from vibe.core.command_engine import CommandEngine
from vibe.core.response_normaliser import ResponseNormaliser
from vibe.core.provider_engine import ProviderEngine, ProviderType
from wizard.services.provider_registry import (
    VibeProviderRegistry,
    TaskMode,
    get_provider_registry,
)
from wizard.services.adapters import OllamaAdapter, MistralAdapter
```

Add initialization in UCODE.__init__():

```python
# Initialize routing components (v1.4.6)
self.input_router = InputRouter(
    command_matcher=match_ucode_command,
    shell_validator=self._validate_shell_safety,
)
self.command_engine = CommandEngine()
self.response_normaliser = ResponseNormaliser()
self.provider_engine = ProviderEngine(
    normaliser=self.response_normaliser,
    timeout=30,
)

# Initialize provider registry
self.provider_registry = get_provider_registry()
self._register_providers()
```

Add provider registration method:

```python
def _register_providers(self) -> None:
    \"\"\"Register available providers with registry.\"\"\"
    # Try registering Ollama (local)
    try:
        import asyncio
        ollama = OllamaAdapter()
        if asyncio.run(ollama.is_available()):
            self.provider_registry.register_provider(
                ProviderType.OLLAMA,
                endpoint="http://127.0.0.1:11434",
                default_model="devstral-small-2",
                priority=0,  # Highest priority (local-first)
            )
            self.logger.info("Registered Ollama provider")
    except Exception as exc:
        self.logger.warning(f"Failed to register Ollama: {exc}")

    # Try registering Mistral (cloud)
    try:
        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key:
            mistral = MistralAdapter(api_key=api_key)
            if asyncio.run(mistral.is_available()):
                self.provider_registry.register_provider(
                    ProviderType.MISTRAL,
                    api_key=api_key,
                    default_model="mistral-small-latest",
                    priority=1,
                )
                self.logger.info("Registered Mistral provider")
    except Exception as exc:
        self.logger.warning(f"Failed to register Mistral: {exc}")
```

Phase 2: Replace _route_input Method
─────────────────────────────────────────────────────────────────────────────────

CURRENT CODE (lines 571-634):
```python
def _route_input(self, user_input: str) -> dict[str, Any]:
    \"\"\"Route input based on prefix: '?', 'OK', '/', or question mode.\"\"\"
    # ... existing prefix-based routing logic ...
```

NEW CODE:
```python
def _route_input(self, user_input: str) -> dict[str, Any]:
    \"\"\"Route input with command-first execution model (v1.4.6).

    Architecture:
    1. InputRouter analyzes input
    2. If ucode command → CommandEngine executes with HARD STOP
    3. If shell command → Execute shell with validation
    4. If natural language → ProviderEngine with normalisation

    This prevents double response bug via explicit short-circuit.
    \"\"\"
    user_input = user_input.strip()
    if not user_input:
        return {\"status\": \"error\", \"message\": \"Empty input\"}

    # Get routing decision
    decision = self.input_router.route(user_input)

    # HARD STOP: If ucode command, execute and return immediately
    if decision.route_type == RouteType.UCODE_COMMAND:
        self.logger.info(
            f\"[ROUTE] ucode command: {decision.command} (confidence={decision.confidence})\"
        )
        result = self.command_engine.execute_ucode(
            decision.command,
            decision.args,
            executor_fn=self._execute_command_impl,
        )

        if result.success:
            return {
                \"status\": \"success\",
                \"command\": decision.command,
                \"output\": result.output,
            }
        else:
            return {
                \"status\": \"error\",
                \"message\": result.error or \"Command execution failed\",
            }

    # Shell command execution
    elif decision.route_type == RouteType.SHELL_COMMAND:
        self.logger.info(f\"[ROUTE] shell command: {decision.raw_input}\")
        return self._execute_shell_command(decision.raw_input)

    # Natural language → Provider
    elif decision.route_type == RouteType.PROVIDER:
        self.logger.info(f\"[ROUTE] provider: {decision.raw_input}\")
        return self._route_to_provider(decision.raw_input)

    else:
        return {
            \"status\": \"error\",
            \"message\": f\"Unknown route type: {decision.route_type}\",
        }


def _execute_command_impl(self, command: str, args: str) -> tuple[bool, str, str]:
    \"\"\"Execute ucode command (adapter for CommandEngine).

    Returns:
        Tuple of (success, stdout, stderr)
    \"\"\"
    try:
        if command in self.commands:
            # Route to existing command handler
            self.commands[command](args)
            return (True, \"\", \"\")
        else:
            return (False, \"\", f\"Unknown command: {command}\")
    except Exception as exc:
        return (False, \"\", str(exc))
```

Phase 3: Add Provider Routing Method
─────────────────────────────────────────────────────────────────────────────────

Add new method to handle provider requests:

```python
def _route_to_provider(self, prompt: str) -> dict[str, Any]:
    \"\"\"Route natural language input to OK Provider.

    Uses ProviderRegistry for capability-based selection.
    Normalises response before any execution.

    Args:
        prompt: Natural language prompt

    Returns:
        Dict with status and response
    \"\"\"
    import asyncio

    # Determine task mode (code, conversation, etc.)
    mode = self._infer_task_mode(prompt)

    # Select provider
    try:
        provider_type, model = self.provider_registry.select_provider_for_task(
            mode=mode,
            prefer_local=True,
        )
    except RuntimeError as exc:
        return {
            \"status\": \"error\",
            \"message\": f\"No provider available: {exc}\",
        }

    # Call provider
    self._ui_line(f\"OK → {provider_type.value} ({model})\", level=\"info\")

    result = asyncio.run(
        self.provider_engine.call_provider(
            provider_type=provider_type.value,
            model=model,
            prompt=prompt,
            system=\"You are a helpful coding assistant for uDOS.\",
        )
    )

    # Record telemetry
    self.provider_registry.record_call(
        provider_type,
        result.success,
        result.execution_time,
        result.status,
    )

    if not result.success:
        return {
            \"status\": \"error\",
            \"message\": result.error or \"Provider call failed\",
        }

    # Display response
    self.renderer.stream_text(result.normalised.text, prefix=\"ok> \")

    # Check for extracted ucode commands (but DO NOT auto-execute)
    if result.normalised.contains_ucode:
        self._ui_line(
            f\"Response contains {len(result.normalised.ucode_commands)} ucode commands\",
            level=\"warn\",
        )
        # Future: Prompt user for confirmation before execution

    return {
        \"status\": \"success\",
        \"command\": \"OK\",
        \"response\": result.normalised.text,
        \"provider\": provider_type.value,
        \"model\": model,
    }


def _infer_task_mode(self, prompt: str) -> str:
    \"\"\"Infer task mode from prompt.

    Simple heuristics for now. Future: Use OK Model for classification.

    Args:
        prompt: User prompt

    Returns:
        Task mode string (code, conversation, etc.)
    \"\"\"
    prompt_lower = prompt.lower()

    code_keywords = {\"write\", \"code\", \"function\", \"class\", \"refactor\", \"debug\"}
    if any(kw in prompt_lower for kw in code_keywords):
        return \"code\"

    return \"conversation\"
```

Phase 4: Replace _dispatch_with_vibe
─────────────────────────────────────────────────────────────────────────────────

CURRENT CODE (lines 476-570):
Handles three-stage dispatch with CommandDispatchService.

NEW CODE:
```python
def _dispatch_with_vibe(self, user_input: str) -> dict[str, Any]:
    \"\"\"Three-stage dispatch with command-first model (v1.4.6).

    This method now delegates to InputRouter for ALL routing decisions.
    The old CommandDispatchService logic is replaced by:
    - InputRouter for routing decisions
    - CommandEngine for ucode execution
    - ProviderEngine for provider calls

    Returns:
        Dict with status, message, and routed result
    \"\"\"
    # Delegate to new routing system
    return self._route_input(user_input)
```

Phase 5: Remove Old Provider Methods
─────────────────────────────────────────────────────────────────────────────────

Methods to deprecate (DO NOT DELETE yet - mark as deprecated):
- _run_ok_request (line 3213) → Add deprecation warning, redirect to _route_to_provider
- _run_ok_local (line 3121) → Add deprecation warning, redirect to ProviderEngine
- _run_ok_cloud → Add deprecation warning, redirect to ProviderEngine

Example deprecation:

```python
def _run_ok_request(self, prompt: str, mode: str, **kwargs) -> None:
    \"\"\"DEPRECATED: Use _route_to_provider instead (v1.4.6).

    This method is kept for backward compatibility but will be removed
    in v1.5.0. It now redirects to the new routing system.
    \"\"\"
    self.logger.warning(
        \"_run_ok_request is deprecated. Use _route_to_provider instead.\"
    )
    result = self._route_to_provider(prompt)
    # Log old-style output for compatibility
    if result.get(\"response\"):
        self._record_ok_output(
            prompt=prompt,
            response=result[\"response\"],
            model=result.get(\"model\", \"unknown\"),
            source=result.get(\"provider\", \"unknown\"),
            mode=mode,
        )
```

════════════════════════════════════════════════════════════════════════════════
TESTING STRATEGY
════════════════════════════════════════════════════════════════════════════════

Test Cases:

1. ucode Command Execution (NO double response)
   Input: "HELP"
   Expected: HELP command executes, NO provider call

2. OK Provider Call (Natural Language)
   Input: "explain this code"
   Expected: Provider call, normalised response, NO ucode execution

3. Shell Command Validation
   Input: "ls -la"
   Expected: Shell validation, safe execution

4. Fuzzy ucode Match with Confirmation
   Input: "hlep" (typo for HELP)
   Expected: Fuzzy match, confirmation prompt, execute on yes

5. Provider Fallback Chain
   Input: "write a hello world function" (Ollama down)
   Expected: Fallback to Mistral cloud provider

6. Timeout Handling
   Input: Long-running provider request
   Expected: Timeout after 30s, clean error message

7. Stream Closing (Ollama)
   Input: "generate code" (Ollama streaming)
   Expected: Response completes, stream closes, NO hanging

════════════════════════════════════════════════════════════════════════════════
ROLLBACK PLAN
════════════════════════════════════════════════════════════════════════════════

If integration fails:

1. Git revert commits
2. Re-enable old _run_ok_request logic
3. Remove new imports
4. Document regression issue
5. Schedule fix for next milestone

Rollback trigger conditions:
- Test suite failure rate > 5%
- ucode commands stop working
- Provider calls fail entirely
- User reports of broken workflow

════════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA
════════════════════════════════════════════════════════════════════════════════

✅ All 514 core tests passing
✅ NO double responses (command + provider)
✅ NO hanging on Ollama requests
✅ Timeout guards working (30s max)
✅ Stream handling correct (explicit close)
✅ Provider fallback working
✅ ucode commands execute with HARD STOP
✅ Natural language routed to provider only

════════════════════════════════════════════════════════════════════════════════
NEXT STEPS
════════════════════════════════════════════════════════════════════════════════

1. Implement Phase 1-5 changes in core/tui/ucode.py
2. Run core test suite: `uv run pytest core/tests -v`
3. Run integration smoke tests
4. Test interactively with Vibe-CLI
5. Validate all success criteria
6. Update DEVLOG.md with results
7. Update AGENTS.md if architecture changes
8. Move tasks to completed.json

════════════════════════════════════════════════════════════════════════════════
End of Integration Plan
════════════════════════════════════════════════════════════════════════════════
"""
