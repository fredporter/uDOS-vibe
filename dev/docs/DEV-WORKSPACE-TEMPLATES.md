# Dev Workspace Templates (Safe Defaults)

These templates are **safe, non-secret** defaults for uDOS contributors. Copy them into your local workspace (do not commit secrets).

## VS Code Extensions Template
Path: `.vscode/extensions.json`

```json
{
  "recommendations": [
    "github.copilot",
    "github.copilot-chat",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ],
  "unwantedRecommendations": []
}
```

## VS Code Tasks Template
Path: `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Health Check",
      "type": "shell",
      "command": "bash",
      "args": [
        "-c",
        "python3 -m core.health status"
      ],
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Start Core TUI",
      "type": "shell",
      "command": "./bin/Launch-uCODE.sh",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "focus": true,
        "clear": true
      },
      "problemMatcher": []
    },
    {
      "label": "Run Shakedown",
      "type": "shell",
      "command": "./bin/Launch-uCODE.sh",
      "args": [
        "memory/tests/shakedown-script.md"
      ],
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "focus": true,
        "clear": true
      },
      "problemMatcher": []
    }
  ]
}
```

## Copilot Instructions Template
Path: `.github/copilot-instructions.md` (or keep local)

```markdown
# Copilot Instructions (Template)

## Role
- Use Copilot for **small, local edits** and **boilerplate**.
- Use Codex for **mission planning**, **multi-file refactors**, and **doc alignment**.

## Guardrails
- Never add secrets, tokens, or credentials.
- Respect the Mission/Move/Step/Milestone model.
- Prefer offline-first assumptions.
```

## Minimal uDOS Workspace Template
Path: `uDOS.code-workspace`

```json
{
  "folders": [
    { "name": "Root", "path": "." },
    { "name": "Core", "path": "core" },
    { "name": "Wizard", "path": "wizard" },
    { "name": "Extensions", "path": "extensions" },
    { "name": "Docs", "path": "docs" },
    { "name": "Sonic", "path": "sonic" },
    { "name": "Dev", "path": "dev" }
  ],
  "settings": {
    "files.exclude": {
      "**/.git": true,
      "**/.DS_Store": true,
      "**/node_modules": true,
      "**/dist": true,
      "**/build": true,
      "memory": true,
      "vault": true
    },
    "search.exclude": {
      "**/node_modules": true,
      "**/dist": true,
      "**/build": true,
      "memory": true,
      "vault": true
    }
  }
}
```
