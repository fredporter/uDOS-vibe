# CI Test Matrix By Profile

Supported CI profile matrix:

| Profile | `uv` extra | Test scope |
| --- | --- | --- |
| `core` | `udos` | `core/tests`, `tests` |
| `wizard` | `udos-wizard` | `wizard/tests`, `core/tests`, `tests` |
| `full` | `udos-full` | `wizard/tests`, `core/tests`, `tests` |

The canonical workflow is defined in:

- `.github/workflows/ci-profiles.yml`

Each profile run also prints a warning-budget summary in CI logs and notices:
- budget: `0`
- observed: parsed from pytest output summary
- visibility: emitted for `core`, `wizard`, and `full`

## Local Reproduction

Core profile:

```bash
uv sync --group dev --extra udos
./scripts/run_pytest_profile.sh core
```

Wizard profile:

```bash
uv sync --group dev --extra udos-wizard
./scripts/run_pytest_profile.sh wizard
```

Full profile:

```bash
uv sync --group dev --extra udos-full
./scripts/run_pytest_profile.sh full
```
