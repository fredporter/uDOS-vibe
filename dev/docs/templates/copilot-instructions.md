# Copilot Instructions (Template)

These are safe, non-secret defaults for uDOS contributors.

## Role
- Use Copilot for **small, local edits** and **boilerplate**.
- Use Codex for **mission planning**, **multi-file refactors**, and **doc alignment**.

## Guardrails
- Never add secrets, tokens, or credentials.
- Respect the Mission/Move/Step/Milestone model.
- Prefer offline-first assumptions.

## Suggested VS Code Settings Snippet

```json
{
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": true
  },
  "github.copilot.editor.enableAutoCompletions": true
}
```
