---
name: ucode-logs
description: >
  Show and filter uDOS system logs. Surfaces recent errors, warnings, and
  activity from the unified log stream. Useful for debugging or auditing
  system behaviour.
allowed-tools: ucode_health ucode_verify
user-invocable: true
---

# ucode-logs

Help the user inspect uDOS log output for debugging or audit purposes.

## What to do

### 1. Get log level preference
Ask (or infer from context) what the user wants to see:
- Recent errors only
- All recent activity (last N lines)
- Logs for a specific subsystem (wizard, binder, dispatcher, etc.)

### 2. Run the LOGS command via tool
Use `ucode_health` with check="logs" to retrieve recent log summary, or
note to the user that detailed logs are available at:
- `memory/logs/` (runtime log directory)
- `VIBE_HOME/logs/vibe.log` (vibe session logs)

### 3. Summarise findings
Present a clean summary:
- Total errors / warnings in the period
- Most recent error with timestamp and context
- Recommended action (REPAIR, VERIFY, or "all clear")

### 4. Offer next steps
If errors found: suggest `/ucode-setup` or running `ucode_repair`.
If clean: confirm system is healthy.

## Notes
- Do not reproduce large raw log dumps — summarise and highlight key issues.
- Respect user privacy: do not share log content outside the session.
