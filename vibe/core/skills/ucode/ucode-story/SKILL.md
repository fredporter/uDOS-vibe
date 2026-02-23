---
name: ucode-story
description: >
  Show the user's active uDOS story — open binders, current tasks, upcoming
  calendar events, and recent completions. A narrative overview of what's
  happening across all active projects.
allowed-tools: ucode_binder ucode_find ucode_health
user-invocable: true
---

# ucode-story

Present a clear narrative overview of the user's current uDOS project landscape.

## What to do

### 1. Check system health (quick)
Call `ucode_health` silently. If uDOS is unreachable, inform the user and stop.

### 2. List open binders
Call `ucode_binder` (action: "list") to get all active project binders.

For each binder found:
- Call `ucode_binder` (action: "status <binder_id>") to get task counts and status.

### 3. Narrate the story
Present results in a friendly, project-manager style:

```
## Your Active Projects

**[Binder Name]** (id: binder-id)
- Tasks: N open, M completed
- Next up: [first todo task title]
- Calendar: [next event if any]

...
```

If no binders exist:
> You have no active projects yet. Use `/ucode-setup` to get started,
> then create your first binder with:
> `BINDER create my-first-project`

### 4. Offer next steps
Ask the user what they'd like to work on, or suggest:
- Opening a specific binder
- Adding a task
- Reviewing completed items
