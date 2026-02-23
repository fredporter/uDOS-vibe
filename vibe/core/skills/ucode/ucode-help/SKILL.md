---
name: ucode-help
description: >
  Show the uDOS ucode command reference. Lists all available ucode commands
  with descriptions and usage examples. Invoke with /ucode-help or ask
  "what ucode commands are available?".
allowed-tools: ucode_find ucode_health
user-invocable: true
---

# ucode-help

You are helping the user understand uDOS ucode commands available in this vibe session.

## What to do

1. Use the `ucode_health` tool to confirm uDOS is reachable and healthy.
2. Present the following command groups clearly:

### Spatial / Navigation
| Command | Description |
|---------|-------------|
| `ucode_map` | Render the spatial map view |
| `ucode_grid` | Show the grid coordinate system |
| `ucode_anchor` | Manage named location bookmarks |
| `ucode_goto` | Navigate to an anchor or coordinate |
| `ucode_find` | Search the spatial index |

### System
| Command | Description |
|---------|-------------|
| `ucode_health` | Full system health report |
| `ucode_verify` | Verify installation integrity |
| `ucode_repair` | Self-heal dependencies and config |
| `ucode_uid` | Show or rotate the device UID |
| `ucode_token` | Manage API access tokens |
| `ucode_viewport` | Report terminal dimensions |

### Data / Projects
| Command | Description |
|---------|-------------|
| `ucode_binder` | Manage project binders (tasks, calendar, completed) |
| `ucode_save` | Persist current state to disk |
| `ucode_load` | Restore state from disk |
| `ucode_seed` | Install or reset framework seed data |
| `ucode_migrate` | Run database/vault migrations |
| `ucode_config` | Read or write configuration values |

### Workspace
| Command | Description |
|---------|-------------|
| `ucode_place` | Manage named workspaces |
| `ucode_scheduler` | Schedule recurring commands |
| `ucode_script` | Run or manage automation scripts |
| `ucode_user` | Manage user profiles and permissions |

### Content / Creative
| Command | Description |
|---------|-------------|
| `ucode_draw` | Render ASCII panel layouts |
| `ucode_sonic` | Ambient sound control |
| `ucode_music` | Music / playlist management |
| `ucode_empire` | Multi-node wizard network management |
| `ucode_destroy` | Wipe data (cache, logs, binder) |
| `ucode_undo` | Undo last N actions from backup |

3. Ask if the user wants to dive into any specific command or group.
