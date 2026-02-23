# Vibe Integration Spec (v1.4)

Status: Historical bridge spec, retained for compatibility.

## Canonical References

Use these docs as the active source of truth:

- `docs/roadmap.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/specs/UCODE-COMMAND-CONTRACT-v1.3.md`
- `docs/specs/VIBE-UCODE-PROTOCOL-v1.4.4.md`
- `docs/howto/VIBE-MCP-INTEGRATION.md`

## Runtime Position

- `vibe` is the primary interactive interface.
- `ucode` command routes to the same command and dispatch surface.
- Dispatch chain remains: `uCODE match -> shell passthrough -> vibe fallback`.

## Legacy Context

Earlier standalone-TUI planning material has been composted:

- `docs/.compost/tui-legacy-2026-02/TUI-MIGRATION-PLAN.md`
- `docs/.compost/tui-legacy-2026-02/VIBE-UCLI-INTEGRATION-GUIDE.md`

