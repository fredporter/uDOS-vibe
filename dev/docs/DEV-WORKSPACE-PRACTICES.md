# Dev Workspace Practices (uDOS Infrastructure)

**Purpose:** This guide defines the dev practices every uDOS contributor must follow to keep the codebase stable and the Vault intact. uDOS can be destroyed and rebuilt; the durable value is the **offline/openbox Vault**.

---

## Principles (Non-Negotiable)

1. **Destroy/Rebuild is normal.** If a workflow or environment degrades, reset and rebuild it instead of patching in place.
2. **Vault is the asset.** Protect `memory/vault/` integrity, exports, and deterministic outputs.
3. **No drift.** Keep docs, tasks, and configs aligned with the current workflow model.
4. **Offline-first, openbox-first.** Never assume network availability; keep local fallbacks viable.
5. **Versioned artifacts, not rounds.** Use version numbers and milestones in filenames and references.

---

## Workflow Model (uDOS Terminology)

- **Mission:** tangible result we must land (no time-boxes).
- **Move:** a counted unit of doing (bundle of steps).
- **Step:** smallest unit of doing (single file, single check, single action).
- **Milestone:** verified achievement composed of moves.

See `docs/DEV-WORKFLOW-v1.3.1.md` for the canonical workflow spine.

---

## Codex + Copilot Collaboration

**Codex = brain.**
- Plans the mission and moves.
- Performs deep refactors, cross-file changes, and doc alignment.
- Enforces repo rules and architecture constraints.

**Copilot = command helper/actioner.**
- Provides inline code suggestions.
- Helps with small edits, local scaffolding, and boilerplate.
- Accelerates tight loops once the plan is defined.

**Recommended flow**
1. Use Codex to define the Mission, Moves, and acceptance checks.
2. Use Copilot for focused code edits or repetitive additions.
3. Return to Codex for review, doc alignment, and cleanup.

---

## VS Code Setup (Recommended)

### Extensions
- GitHub Copilot
- GitHub Copilot Chat
- (Optional) ESLint / Prettier / Ruff, depending on project lane

### Suggested VS Code Settings
Create or update `.vscode/settings.json` in your local workspace (do not commit secrets):

```json
{
  "editor.formatOnSave": true,
  "editor.inlineSuggest.enabled": true,
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": true
  },
  "github.copilot.editor.enableAutoCompletions": true
}
```

### Copilot Sign-In
1. In VS Code, open the Command Palette → `Copilot: Sign In`.
2. Authorize with GitHub.
3. Verify suggestions appear in editor.

---

## Codex Setup (Local Workflow)

1. Open Codex in the uDOS repo root.
2. Keep the Mission/Move/Step model as the decision spine.
3. Ask Codex to review diff scopes before large changes.
4. Use Codex for doc sync whenever a workflow changes.

---

## Dev Workspace Instruction Template

Use this template when starting a new dev effort in uDOS:

```markdown
# Dev Workspace Instruction — <Mission Name>

## Mission
- What we are doing:
- Tangible result:

## Moves
1. <Move name> — expected artifact:
   - Steps:
     - [ ] <Step 1>
     - [ ] <Step 2>
2. <Move name> — expected artifact:
   - Steps:
     - [ ] <Step 1>
     - [ ] <Step 2>

## Acceptance Checks
- [ ] <Check 1>
- [ ] <Check 2>

## Vault/Memory Updates
- [ ] <If applicable, which vault path or memory log gets updated>

## Cleanup
- [ ] Update docs / indices
- [ ] Remove temp files
```

---

## Repository Hygiene Rules

- **Docs:** Use `/docs` for canonical docs. Use `/dev/wiki` for scaffold-only guidance.
- **Roadmap specs:** Keep `/docs/roadmap-spec/` local-only and never archive that folder.
- **Archiving:** Move old docs to `.archive/` when they’re obsolete; never archive roadmap-spec docs.
- **Versioned naming:** Use `vX.Y.Z` naming for plans and summaries; avoid “round” naming.
- **No secrets:** Never commit credentials or personal tokens.

---

## Guardrails for uDOS Quality

- Align changes with `docs/DEV-WORKFLOW-v1.3.1.md`.
- Keep `docs/specs/v1.3.1-milestones.md` current.
- Ensure any new workflow language uses Mission/Move/Step/Milestone.
- Confirm any new feature respects offline-first defaults.

---

## Quick Reminder

uDOS can be rebuilt. The Vault is the asset. Protect deterministic outputs and the offline/openbox path.

---

## Templates

Use the safe, non-secret templates here:

- `dev/wiki/DEV-WORKSPACE-TEMPLATES.md`
