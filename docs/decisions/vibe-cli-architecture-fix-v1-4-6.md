# Vibe-CLI Architecture Fix — v1.4.6

Date: 2026-02-24
Status: Implementation Required
Priority: High

---

## Problem Statement

Vibe-CLI currently exhibits multiple architectural issues:

1. **Hanging/Blocking:** Vibe-CLI hangs or blocks during provider interactions
2. **Double Response:** Both ucode execution AND provider response are returned
3. **Ollama Failures:** Ollama integration never worked reliably
4. **Provider Selection:** Multi-provider routing is not deterministic
5. **Stream Issues:** Streaming responses don't close properly

## Root Cause Analysis

Current architecture is **assistant-first** instead of **command-first**:

```python
# Current (broken) flow:
User input
  ↓
Send to provider
  ↓
Parse response
  ↓
Maybe execute ucode
  ↓
Maybe print response
  ↓
(both happen = double response)
```

This violates the deterministic execution model.

---

## Required Architecture

### Command-First Execution Model

```python
# Correct flow:
User input
  ↓
Command Detector
  ↓
IF valid ucode:
    parse → execute → return
    HARD STOP
ELSE IF ucode syntax error:
    print error
    HARD STOP
ELSE:
    provider call → normalise → return
```

### Execution Priority

1. **ucode commands** (deterministic, local)
2. **Shell commands** (if allowed, validated)
3. **Provider fallback** (generative, remote)

NO simultaneous execution.
NO double outputs.

---

## Implementation Requirements

### 1. Input Router Module

Location: `vibe/core/input_router.py`

```python
class InputRouter:
    def route(self, user_input: str) -> RouteDecision:
        """
        Determine routing destination.

        Returns:
            RouteDecision with one of:
            - UCODE_COMMAND
            - SHELL_COMMAND
            - PROVIDER_FALLBACK
            - SYNTAX_ERROR
        """
```

### 2. Command Engine Module

Location: `vibe/core/command_engine.py`

```python
class CommandEngine:
    def execute_ucode(self, command: str) -> ExecutionResult:
        """Execute ucode command with short-circuit."""
        # Execute and return
        # NO provider interaction
```

### 3. OK Provider Engine Module

Location: `vibe/core/provider_engine.py`

```python
class OKProviderEngine:
    def call_provider(self, prompt: str) -> ProviderResponse:
        """
        Call provider with:
        - Timeout guards
        - Stream handling
        - Response normalisation
        - Error recovery
        """
```

### 4. Response Normaliser Module

Location: `vibe/core/response_normaliser.py`

```python
class ResponseNormaliser:
    def normalise(self, raw_response: str) -> NormalisedResponse:
        """
        Normalise provider response:
        - Strip markdown wrappers
        - Extract ucode commands
        - Validate syntax
        - Prevent shell injection
        """
```

---

## Vibe-CLI Execution Flow (Corrected)

### Phase 1: Input Detection

```python
user_input = get_input()
route = InputRouter().route(user_input)
```

### Phase 2: Short-Circuit Execution

```python
if route.type == RouteType.UCODE_COMMAND:
    result = CommandEngine().execute_ucode(route.command)
    print(result)
    return  # HARD STOP

if route.type == RouteType.SYNTAX_ERROR:
    print(route.error)
    return  # HARD STOP
```

### Phase 3: Provider Fallback (Only If Not Command)

```python
if route.type == RouteType.PROVIDER_FALLBACK:
    raw_response = OKProviderEngine().call_provider(user_input)
    normalised = ResponseNormaliser().normalise(raw_response)

    if normalised.contains_ucode:
        # Provider suggested a ucode command
        # Validate before executing
        result = CommandEngine().execute_ucode(normalised.ucode)
        print(result)
    else:
        print(normalised.text)
```

---

## Provider Abstraction Contract

### Provider Adapter Interface

All providers must implement:

```python
class ProviderAdapter(Protocol):
    def call(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Standard provider call interface."""
```

### Provider Registry

Location: `wizard/services/provider_registry.py`

```python
class ProviderRegistry:
    def register(self, name: str, adapter: ProviderAdapter):
        """Register a provider adapter."""

    def get(self, name: str) -> ProviderAdapter:
        """Get provider by name."""

    def route(self, task_type: str) -> ProviderAdapter:
        """Route to best provider for task type."""
```

### Provider Capabilities

Each provider must declare:

- Model name
- Max tokens
- Streaming support
- Structured output support
- Cost tier

---

## Ollama-Specific Fixes

### Issues

1. Streaming doesn't close properly
2. Context window overflow
3. Timeout handling broken
4. API format inconsistency

### Solutions

1. **Stream Closing:**
   ```python
   def _consume_stream(self, response):
       try:
           for chunk in response.iter_lines():
               if not chunk:
                   break
               yield chunk
       finally:
           response.close()  # Explicit close
   ```

2. **Timeout Guards:**
   ```python
   timeout = httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)
   ```

3. **API Format Detection:**
   ```python
   # Try /api/chat first (newer Ollama)
   # Fallback to /api/generate (older Ollama)
   ```

---

## Testing Requirements

### Unit Tests

- [ ] Input router correctly identifies ucode commands
- [ ] Short-circuit logic prevents double execution
- [ ] Provider normaliser strips markdown correctly
- [ ] Stream timeout handling works

### Integration Tests

- [ ] Ollama provider doesn't hang
- [ ] Multi-provider fallback works
- [ ] No double responses occur
- [ ] ucode commands execute before provider call

### Manual Tests

- [ ] Type `HELP` → executes immediately (no provider call)
- [ ] Type `? explain this` → calls provider only
- [ ] Type `/STATUS` → executes as ucode
- [ ] Provider response with ucode → validates before execution

---

## Migration Plan

### Phase 1: Isolate Modules (Week 1)

- Extract InputRouter
- Extract CommandEngine
- Extract ProviderEngine
- Add tests for each

### Phase 2: Implement Short-Circuit (Week 1)

- Add HARD STOP after ucode execution
- Remove simultaneous execution paths
- Validate no double responses

### Phase 3: Provider Abstraction (Week 2)

- Implement ProviderAdapter interface
- Migrate Ollama to adapter
- Migrate Mistral to adapter
- Add provider registry

### Phase 4: Normalisation Layer (Week 2)

- Implement ResponseNormaliser
- Add markdown stripping
- Add ucode extraction
- Add validation logic

### Phase 5: Testing & Validation (Week 3)

- Full test suite
- Manual testing
- Performance benchmarks
- Documentation

---

## Success Criteria

- ✅ No hanging/blocking
- ✅ No double responses
- ✅ Ollama works reliably
- ✅ Provider selection is deterministic
- ✅ Streams close properly
- ✅ 100% test pass rate
- ✅ ucode commands execute < 100ms
- ✅ Provider calls have proper timeout

---

## Files to Modify

### New Files

- `vibe/core/input_router.py`
- `vibe/core/command_engine.py`
- `vibe/core/provider_engine.py`
- `vibe/core/response_normaliser.py`
- `wizard/services/provider_registry.py`
- `wizard/services/adapters/ollama_adapter.py`
- `wizard/services/adapters/mistral_adapter.py`

### Modified Files

- `core/tui/ucode.py` (use new routing)
- `wizard/routes/ucode_routes.py` (use new provider engine)
- `wizard/services/vibe_service.py` (refactor to adapter)
- `wizard/services/ollama_service.py` (refactor to adapter)

### Test Files

- `core/tests/test_input_router.py`
- `core/tests/test_command_engine.py`
- `wizard/tests/test_provider_engine.py`
- `wizard/tests/test_provider_registry.py`
- `wizard/tests/test_ollama_adapter.py`

---

## References

- [AGENTS.md](../../AGENTS.md) — Root governance
- [vibe/AGENTS.md](../../vibe/AGENTS.md) — Vibe subsystem rules
- [OK-update-v1-4-6.md](./OK-update-v1-4-6.md) — Policy document
- [VIBE-UCODE-PROTOCOL-v1.4.4.md](../specs/VIBE-UCODE-PROTOCOL-v1.4.4.md) — Dispatch spec

---

End of Document
