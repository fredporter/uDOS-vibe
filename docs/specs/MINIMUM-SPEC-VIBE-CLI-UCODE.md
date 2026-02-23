# Minimum Spec for vibe-cli with uCode Addon (Offline/Online Pathways)

## 1. Overview

This document defines the minimum requirements and operational pathways for `vibe-cli` with a custom `uCode` command set (`UCODE`).
It guarantees a usable experience in both online and offline environments, with explicit local guidance when no network is available.

## 2. Minimum Specifications

| Component | Requirement |
|---------|-------------|
| OS | Linux/macOS/Windows 10+ (x86/ARM) |
| CPU | 2 cores (x86/ARM) |
| RAM | 4 GB |
| Storage | 5 GB free (SSD recommended) |
| Network | Optional (see pathways) |
| Dependencies | Python 3.12+, vibe-cli, uCode addon |

## 3. Operational Pathways

### A. With Network Access

- Primary path: `UCODE` commands with vibe-cli.
- Fallback path: cloud AI provider API responses.
- Features:
  - Full `uCode` command set (`UCODE --help`).
  - Cloud AI for complex queries.
  - System introspection and `uDOS` documentation access.

### B. Without Network Access

- Primary path: `UCODE` commands only.
- Fallback path: minimal local AI-inspired behavior.
- Features:
  - Preloaded demo scripts for common tasks.
  - Interactive help for `uCode` and `uDOS` commands.
  - System capability reporting (CPU, RAM, storage, OS).
  - Offline documentation for `uCode` and `uDOS`.

## 4. Minimal AI-Inspired Fallback (No Network)

### A. Demo Scripts

- Purpose: simulate AI-like answers for common requests.
- Commands:
  - `UCODE DEMO LIST`
  - `UCODE DEMO RUN <script>`
- Storage path: `~/.vibe-cli/ucode/demos/`
- Templated responses include:
  - "How do I use uCode?" -> show `UCODE --help`
  - "What can my system run?" -> show system specs and compatible command families

### B. System Education

- Commands:
  - `UCODE SYSTEM INFO` -> OS, CPU, RAM, storage + minimum-spec pass/fail report
  - `UCODE DOCS` -> local docs view/query
  - `UCODE CAPABILITIES` -> available extensions based on current setup

### C. Offline Documentation

- Storage path: `~/.vibe-cli/ucode/docs/`
- Supported formats: Markdown, JSON
- Required content:
  - `uCode` command reference
  - `uDOS` workflow examples
  - Troubleshooting guides

## 5. Example Workflow (No Network)

```bash
user> UCODE "How do I parse a file with uCode?"

1. Local demo script:
   UCODE DEMO RUN parse_file
2. Documentation:
   UCODE DOCS --query "parse file"
3. System capabilities:
   UCODE CAPABILITIES --filter "file"
```

## 6. Implementation Steps

1. Install vibe-cli + uCode addon:

```bash
uv add vibe-cli ucode-addon
UCODE --setup
```

2. Populate offline resources:
- Copy demo scripts to `~/.vibe-cli/ucode/demos/`
- Store docs in `~/.vibe-cli/ucode/docs/`

3. Configure fallback in vibe-cli:
- When network is unavailable, route requests in this order:
  - Demo scripts
  - Documentation lookup
  - System introspection
  - Capability checks

4. First-run guidance in offline mode:

```text
No network detected. Using offline mode. Try:
- UCODE DEMO LIST
- UCODE DOCS --query <text>
- UCODE SYSTEM INFO
- UCODE CAPABILITIES --filter <text>
```

## 7. Limitations

- No dynamic cloud-style responses in offline mode.
- Demo scripts and docs are static until refreshed via `UCODE UPDATE` when online.
- Offline bundle signatures are local by default (HMAC key under `~/.vibe-cli/ucode/bundles/` unless overridden by `UCODE_BUNDLE_SIGNING_KEY`).
- Offline usage metrics are local-only under `~/.vibe-cli/ucode/metrics/` (`usage-events.jsonl`, `usage-summary.json`).

## 8. Extensibility

- Users can add custom demos/docs under `~/.vibe-cli/ucode/`.
- Plugins can extend capability reporting, for example:
  - `UCODE plugin install <name>`
  - `UCODE plugin list`

## 9. Example Offline Session

```bash
user> UCODE "What is uDOS?"
# Output:
"uDOS is a documentation system for uCode. Offline docs available:
- UCODE DOCS --section 'uDOS'"

user> UCODE DEMO LIST
# Output:
1. parse_file
2. system_check
3. format_converter
```

## 10. Pathway Comparison

| Feature | With Network | Without Network |
|-------|--------------|-----------------|
| AI Responses | Yes (cloud API) | No (demo scripts only) |
| uCode Commands | Yes | Yes |
| System Introspection | Yes | Yes |
| Documentation | Yes (online/offline) | Yes (offline only) |
| Dynamic Help | Yes | No (static docs/demos) |

## 11. Minimum Spec Validation Contract

`UCODE SYSTEM INFO` must include:

- Minimum target line: `2 cores / 4.0 GB RAM / 5.0 GB free`.
- Overall status: `PASS` or `FAIL`.
- Per-resource status:
  - CPU pass/fail against `>=2` cores
  - RAM pass/fail against `>=4.0 GB`
  - Storage pass/fail against `>=5.0 GB free`

Structured response payload must expose the same results under:
- `system.minimum_spec.targets`
- `system.minimum_spec.result`

Field validation (rebaseline round) must expose:
- `system.field_validation.round`
- `system.field_validation.sample_size`
- `system.field_validation.rebaseline_targets`

Current rebaseline after first field validation round (2026-02-22):
- CPU: `2` cores
- RAM: `4.0` GB
- Storage: `5.0` GB free
