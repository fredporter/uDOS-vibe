# How to Use Vibe Skills in uDOS-Vibe

You have **5 uDOS skills** available. Here's how to use them:

## 1. **ucode-help** — Documentation & Command Lookup
```
Type in Vibe:
/ucode-help COMMAND_NAME

Examples:
/ucode-help health     → Learn about the health check command
/ucode-help setup      → How to initialize the environment
/ucode-help repair     → Fix broken configurations
```

## 2. **ucode-setup** — Interactive First-Run Wizard
```
/ucode-setup

This will:
- Ask for your username
- Set your timezone
- Configure location
- Initialize vault structure
```

## 3. **ucode-story** — Read & Execute Narrative Content
```
/ucode-story STORY_ID

Examples:
/ucode-story intro     → Welcome to uDOS narrative
/ucode-story tutorial  → Interactive tutorial
```

## 4. **ucode-dev** — Developer Mode & Debugging
```
/ucode-dev

Shows:
- Available tools
- Skill status
- Configuration details
- System diagnostics
```

## 5. **ucode-logs** — View Diagnostic Logs
```
/ucode-logs

Returns:
- Recent system logs
- Error messages
- Performance metrics
```

---

## How to Invoke Tools Directly

If you want tools (not skills), use natural language prompts like:

```
"Check the system health"
→ Will use ucode_health tool

"Run the backup script"
→ Will use ucode_run tool

"Help me set up"
→ Will use ucode_setup tool
```

---

## Troubleshooting

### Tools Not Showing Up?
1. Make sure the wizard MCP server is running:
   ```bash
   uv run --project . wizard/mcp/mcp_server.py --tools
   ```

2. Then run vibe:
   ```bash
   vibe trust && vibe
   ```

### Skills Asking for Input?
Just type what they ask for. Skills are interactive and guide you through workflows.

### Want to See All Available Tools?
Ask Vibe:
```
"What tools are available?"
```

---

## Quick Start Guide

### Option A: Use Skills (Recommended for First Time)
```bash
vibe trust && vibe
# Then type: /ucode-help

# Or try the setup:
# Type: /ucode-setup
```

### Option B: Use Tools via Natural Language
```bash
vibe trust && vibe
# Then ask: "Check my system health"
# Or: "List available commands"
```

### Option C: Use Raw Commands (Advanced)
```bash
vibe trust && vibe
# Ask: "Run ucode_health with check='system'"
# Or: "Call ucode_run with script='backup'"
```

---

## What Tools Are Available?

You have 42 uDOS tools:

### System (6)
- Health checks, verification, repair, UID management, tokens, viewport

### Navigation (5)
- Map, grid, anchor, goto, find

### Data (6)
- Binder, save, load, seed, migrate, config

### Execution (4)
- Place, scheduler, script, user

### Content (6)
- Draw, sonic, music, empire, destroy, undo

### Bonus (9)
- Help, setup, run, story, talk, read, play, print, format

### Specialized (5)
- Watch, export, import, notify, bench

---

## Next Steps

1. **Try a skill first:**
   ```
   /ucode-help
   ```

2. **Ask for system status:**
   ```
   "Check my health"
   ```

3. **Set up your environment:**
   ```
   /ucode-setup
   ```

4. **Read the story/tutorial:**
   ```
   /ucode-story intro
   ```
