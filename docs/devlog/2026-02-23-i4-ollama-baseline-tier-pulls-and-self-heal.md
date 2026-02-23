# 2026-02-23 I4: Ollama Baseline Tier Pulls + Health/Self-Heal

## Scope

Complete I4 from `docs/roadmap.md`: stabilize Wizard-aligned Ollama model baseline by tier, and add explicit readiness/fallback diagnostics in self-heal flows.

## Changes

- Installer tier pull profiles and preflight output:
  - Updated `bin/install-udos-vibe.sh` with canonical Wizard-aligned baseline catalogs.
  - Added tier profile helpers for model selection:
    - tier2: `devstral-small-2`, `mistral`, `llama3.2`, `qwen3`
    - tier3: `mistral`, `devstral-small-2`, `llama3.2`, `qwen3`, `codellama`, `phi3`, `gemma2`, `deepseek-coder`
  - Added `ollama_recommended_models` to `--preflight-json` output.
  - Persisted selected profile to `.env` via `VIBE_OLLAMA_RECOMMENDED_MODELS`.
  - Updated interactive model list to Wizard baseline and added `recommended` selection path.
- Self-heal model readiness diagnostics:
  - Extended `core/services/self_healer.py`:
    - detect missing configured local default model (`OLLAMA_DEFAULT_MODEL` / `VIBE_ASK_MODEL`, default `devstral-small-2`)
    - emit repairable issue with action `pull_ollama_model`
    - implement auto-repair by executing `ollama pull <model>` and re-validating reachability
- Wizard self-heal API contract:
  - Extended `wizard/routes/self_heal_routes.py`:
    - tier-aware required model list from `VIBE_OLLAMA_RECOMMENDED_MODELS` or tier defaults
    - include configured default model in required-model checks
    - `/api/self-heal/status` now returns:
      - `required_models`
      - `configured_default_model`
      - `missing_default_model`
    - remediation hints now produce pull commands for all missing models
- Provider route catalog alignment:
  - Updated `wizard/routes/provider_routes.py` so authenticated `/api/providers/ollama/models/available` uses `get_popular_models(include_installed=True)` (same canonical source as public route).

## Tests Added/Updated

- `core/tests/install_preflight_tier_gates_test.py`
  - assert `ollama_recommended_models` for auto-selected tier2 and tier3 preflight payloads
- `core/tests/self_healer_boundary_test.py`
  - missing-default-model issue is emitted when default model is absent from Ollama tags
  - unreachable `/api/tags` does not produce false-positive model-missing issue
- `wizard/tests/self_heal_routes_recovery_test.py`
  - `ollama_recover` includes configured default model in `required`/`missing`
  - `/api/self-heal/status` exposes `configured_default_model` and `missing_default_model`
- `wizard/tests/provider_health_routes_test.py`
  - `/api/providers/ollama/models/available` uses canonical catalog source and dynamic categories

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
  core/tests/install_preflight_tier_gates_test.py \
  core/tests/self_healer_boundary_test.py \
  wizard/tests/self_heal_routes_recovery_test.py \
  wizard/tests/provider_health_routes_test.py
```

## Result

- PASS: `15 passed in 2.50s`
- FAIL: `0`
- WARN: `0`

## Missed-TODO Sweep (Touched Files)

- `bin/install-udos-vibe.sh`: no actionable TODO/FIXME markers.
- `core/services/self_healer.py`: no actionable TODO/FIXME markers.
- `wizard/routes/self_heal_routes.py`: no actionable TODO/FIXME markers.
- `wizard/routes/provider_routes.py`: no actionable TODO/FIXME markers.

## Remaining Risk

- I4 validation was targeted. Full RC1 profile-matrix runs (`core`, `wizard`, `full`) remain pending under I7 readiness validation.
