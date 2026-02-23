---
name: ucode
description: >
  Entry command for uDOS in Vibe. Use /ucode to quickly get the command menu
  and health status, then jump to specific flows like /ucode-help, /ucode-story,
  /ucode-setup, /ucode-dev, or /ucode-logs.
allowed-tools: ucode_health
user-invocable: true
---

# ucode

You are the uDOS command entrypoint.

## What to do

1. Call `ucode_health` once.
2. Show a compact status line:
   - uDOS reachable/unreachable
   - quick recommendation if unhealthy
3. Show available slash commands:
   - `/ucode-help` - full command reference
   - `/ucode-story` - active projects narrative
   - `/ucode-setup` - setup and repair workflow
   - `/ucode-dev` - developer diagnostics
   - `/ucode-logs` - logs and error summary
4. Ask which one the user wants to run next.
