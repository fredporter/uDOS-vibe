# 2026-02-23 I3: Provider Schema + Fallback Policy

## Scope

Complete I3 from `docs/roadmap.md`: canonical provider schema and deterministic failover policy with integration coverage.

## Changes

- Added canonical cloud-provider policy module:
  - `core/services/cloud_provider_policy.py`
- Implemented canonical contracts for:
  - `mistral`
  - `openrouter`
  - `openai`
  - `anthropic`
  - `gemini`
- Added deterministic provider chain resolution:
  - explicit: `VIBE_CLOUD_PROVIDER_CHAIN`
  - fallback envs: `VIBE_PRIMARY_CLOUD_PROVIDER`, `VIBE_SECONDARY_CLOUD_PROVIDER`
  - default chain when unset: `mistral -> openrouter -> openai -> anthropic -> gemini`
- Added provider request preparation + response parsing by API style:
  - OpenAI chat-completions style
  - Anthropic messages style
  - Gemini generateContent style
- Added failover reason classifier and policy:
  - missing auth
  - auth error (401/403)
  - rate limit (429)
  - unreachable (connection + 5xx class)
- Wired `uCODE` cloud execution to use deterministic direct-provider chain when Wizard cloud path is unavailable:
  - updated `core/tui/ucode.py`
  - preserves existing quota message for explicit 429 cloud-gateway response
  - logs failover attempt summary when fallback succeeds

## Integration Coverage Added

- `core/tests/cloud_provider_policy_test.py`
  - chain resolution
  - request/response parsing for OpenAI + Gemini styles
  - failover reason classification
- `core/tests/ucode_setup_network_boundary_test.py`
  - secondary-provider failover on primary rate limit
  - secondary-provider failover on primary unreachable
  - no-key cloud error path
  - existing quota mapping coverage retained

## Validation Commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  core/tests/cloud_provider_policy_test.py \
  core/tests/ucode_setup_network_boundary_test.py -q
```

## Result

- PASS: `13 passed in 1.70s`
- FAIL: `0`
- WARN: `0`

## Remaining Risk

- Wizard-side provider contracts remain a separate surface and should be aligned in I4/I5 so route behavior is consistent across direct core fallback and Wizard gateway mode.
