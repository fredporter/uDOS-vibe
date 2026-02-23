# uDOS v1.4.5 +Vibe Tools Reference

Complete reference for all 37 uDOS tools available in uDOS v1.4.5 +Vibe.

---

## Quick Start

### 1. Enable uDOS Tools

When launching vibe, enable ucode tools:

```bash
vibe --enabled-tools "ucode*" --prompt "Your question here"
```

Or interactively:
```bash
vibe --enabled-tools "ucode*"
> /ucode-help          # See all available commands
> /ucode-setup        # Initialize uDOS
```

### 2. Get Help

```bash
> What ucode commands are available?
> Help me understand the HEALTH command
> How do I save something to the vault?
```

### 3. Common Workflows

**Check system health:**
```bash
> Run a health check on my system
```

**Save and load data:**
```bash
> Save my current state to the vault
> Load my saved state from the vault
```

**Execute automation:**
```bash
> Run the backup script
> Execute my migration script with --dry-run
```

---

## Tools by Category

### System & Health (8 tools)

#### `ucode_health`
Check uDOS system health and subsystem status.

**Usage:**
```python
ucode_health(check="")           # Full health report
ucode_health(check="db")         # Check database subsystem
ucode_health(check="wizard")     # Check wizard subsystem
ucode_health(check="vault")      # Check vault subsystem
```

**Examples:**
- "Run a full health check"
- "Check if the database is healthy"
- "Is the wizard system running?"

---

#### `ucode_verify`
Verify installation integrity and configuration.

**Usage:**
```python
ucode_verify(check="")           # Full verification
ucode_verify(check="dependencies")  # Check deps
```

**Examples:**
- "Verify my uDOS installation"
- "Check that all dependencies are installed"

---

#### `ucode_repair`
Self-heal the uDOS installation.

**Usage:**
```python
ucode_repair(target="all")       # Repair everything
ucode_repair(target="config")    # Fix config only
ucode_repair(target="db")        # Rebuild database
```

**Examples:**
- "Fix my installation"
- "Repair the database"

---

#### `ucode_help` ⭐
Get help with uDOS commands (CRITICAL for discovery).

**Usage:**
```python
ucode_help(command="")           # List all commands
ucode_help(command="HEALTH")     # Help for HEALTH
ucode_help(topic="data")         # Commands for data work
```

**Examples:**
- "What commands are available?"
- "How do I use the BINDER command?"
- "Show me all data-related tools"

---

#### `ucode_uid`
Manage the device/user UID.

**Usage:**
```python
ucode_uid(action="show")         # Show current UID
ucode_uid(action="rotate")       # Generate new UID
```

**Examples:**
- "What's my device UID?"
- "Generate a new user ID"

---

#### `ucode_token`
Manage API access tokens.

**Usage:**
```python
ucode_token(action="generate")   # Create new token
ucode_token(action="list")       # Show all tokens
ucode_token(action="revoke", token_id="abc")
```

**Examples:**
- "Generate a new API token"
- "List all my access tokens"
- "Revoke this token"

---

#### `ucode_viewport`
Report terminal dimensions and capabilities.

**Usage:**
```python
ucode_viewport()                 # Get terminal size
```

**Examples:**
- "What's my terminal size?"
- "How many rows and columns do I have?"

---

### Navigation & Spatial (6 tools)

#### `ucode_map`
Show spatial file tree and navigation map.

**Usage:**
```python
ucode_map(area="")               # Full map
ucode_map(area="vault")          # Vault area
ucode_map(area="workspace")      # Workspace area
```

**Examples:**
- "Show me the map"
- "Display the vault structure"

---

#### `ucode_grid`
Show grid coordinate system.

**Usage:**
```python
ucode_grid(mode="show")          # Show grid
ucode_grid(mode="toggle")        # Toggle grid display
```

---

#### `ucode_anchor`
Mark and manage named location bookmarks.

**Usage:**
```python
ucode_anchor(action="list")      # Show bookmarks
ucode_anchor(action="add", name="inbox")
ucode_anchor(action="delete", name="inbox")
```

**Examples:**
- "List all my bookmarks"
- "Bookmark this location as 'inbox'"

---

#### `ucode_goto`
Navigate to a marked location.

**Usage:**
```python
ucode_goto(location="inbox")     # Go to bookmark
ucode_goto(location="0,5")       # Go to coordinates
```

**Examples:**
- "Go to my inbox"
- "Navigate to the vault"

---

#### `ucode_find`
Search files and content.

**Usage:**
```python
ucode_find(query="backup")       # Search for "backup"
ucode_find(query="python", type_="file")
ucode_find(query="error", type_="log")
```

**Examples:**
- "Find all files containing 'backup'"
- "Search for Python files"
- "Look for error messages in logs"

---

### Data & Knowledge (7 tools)

#### `ucode_binder`
Manage project binders (tasks, calendar, completed).

**Usage:**
```python
ucode_binder(action="list")      # Show all binders
ucode_binder(action="open", binder_id="project-x")
ucode_binder(action="create", name="new-project")
ucode_binder(action="status", binder_id="project-x")
```

**Examples:**
- "List all my project binders"
- "Open the project-x binder"
- "Create a new project called 'feature-release'"

---

#### `ucode_save`
Persist current state to vault.

**Usage:**
```python
ucode_save(path="vault/backups")     # Save to path
ucode_save(path="vault/backups", compress=True)
```

**Examples:**
- "Save my state to the vault"
- "Create a backup of everything"

---

#### `ucode_load`
Restore state from vault.

**Usage:**
```python
ucode_load(path="vault/backups/latest")
ucode_load(path="vault/backups", restore_date="2026-02-20")
```

**Examples:**
- "Load my last saved state"
- "Restore from February 20"

---

#### `ucode_seed`
Seed vault with bootstrap templates and data.

**Usage:**
```python
ucode_seed(template="default")   # Use default templates
ucode_seed(template="advanced")  # Use advanced templates
```

**Examples:**
- "Initialize my vault with templates"
- "Seed the vault with starter content"

---

#### `ucode_migrate`
Run database and vault migrations.

**Usage:**
```python
ucode_migrate(action="check")    # Check for pending
ucode_migrate(action="run")      # Run migrations
ucode_migrate(action="rollback") # Undo migrations
```

**Examples:**
- "Check for pending migrations"
- "Run database migrations"

---

#### `ucode_config`
Manage configuration values.

**Usage:**
```python
ucode_config(action="show")      # Show all config
ucode_config(action="get", key="vault.path")
ucode_config(action="set", key="vault.path", value="/data/vault")
```

**Examples:**
- "Show all configuration"
- "What's my vault path?"
- "Set the vault path to /custom/vault"

---

### Workspace & Execution (7 tools)

#### `ucode_place`
Manage named workspace places.

**Usage:**
```python
ucode_place(action="list")       # Show all places
ucode_place(action="open", name="project-a")
ucode_place(action="create", name="new-place")
ucode_place(action="switch", name="project-a")
```

**Examples:**
- "List all my workspaces"
- "Switch to project-a"
- "Create a new workspace"

---

#### `ucode_scheduler`
Schedule recurring tasks and automation.

**Usage:**
```python
ucode_scheduler(action="list")       # Show schedules
ucode_scheduler(action="create", command="BACKUP", cron="0 2 * * *")
ucode_scheduler(action="delete", job_id="backup-nightly")
```

**Examples:**
- "List all scheduled tasks"
- "Schedule a nightly backup"
- "Stop the weekly report job"

---

#### `ucode_script`
Execute or manage automation scripts.

**Usage:**
```python
ucode_script(action="list")      # Show scripts
ucode_script(action="run", script="backup")
ucode_script(action="show", script="backup")
ucode_script(action="edit", script="backup")
```

**Examples:**
- "List all available scripts"
- "Run the backup script"
- "Show me the backup script"

---

#### `ucode_setup` ⭐
Interactive setup wizard.

**Usage:**
```python
ucode_setup(step="wizard")       # Interactive setup
ucode_setup(step="quick")        # Use defaults
ucode_setup(step="config", confirm=True)
```

**Examples:**
- "Set up uDOS"
- "Run the setup wizard"
- "Do a quick setup with defaults"

---

#### `ucode_run` ⭐
Execute scripts and automation.

**Usage:**
```python
ucode_run(script="backup")       # Run backup script
ucode_run(script="sync", args="--all")
ucode_run(script="migrate", dry_run=True)
```

**Examples:**
- "Run the backup script"
- "Execute the sync with --all flag"
- "Do a dry-run of the migration"

---

#### `ucode_user`
Manage user profiles and permissions.

**Usage:**
```python
ucode_user(action="show")        # Show current user
ucode_user(action="list")        # List all users
ucode_user(action="create", username="alice")
ucode_user(action="switch", username="alice")
```

**Examples:**
- "Who am I?"
- "List all users"
- "Switch to the alice user"

---

### Content & Creative (13 tools)

#### `ucode_story` ⭐
Read and interact with narrative content.

**Usage:**
```python
ucode_story(action="list")       # Show available stories
ucode_story(action="read", story_id="adventure-1")
ucode_story(action="resume", story_id="adventure-1")
ucode_story(action="status")     # Show active story
```

**Examples:**
- "List all available stories"
- "Tell me a story"
- "Continue where I left off"

---

#### `ucode_talk` ⭐
Interact with NPCs and characters.

**Usage:**
```python
ucode_talk(target="guide")           # Talk to NPC
ucode_talk(target="merchant", message="What do you have?")
```

**Examples:**
- "Talk to the guide"
- "Ask the merchant about prices"

---

#### `ucode_read` ⭐
Read markdown and text content from vault.

**Usage:**
```python
ucode_read(path="docs/guide.md")
ucode_read(path="vault/notes/project", section="Installation")
```

**Examples:**
- "Read the installation guide"
- "Show me the troubleshooting section"

---

#### `ucode_play` ⭐
Play interactive games.

**Usage:**
```python
ucode_play()                     # List available games
ucode_play(game="adventure", action="start")
ucode_play(game="roguelike", action="continue")
ucode_play(game="puzzle", action="status")
```

**Examples:**
- "What games can I play?"
- "Start a new adventure game"
- "Resume my roguelike run"

---

#### `ucode_draw`
Render ASCII art and diagrams.

**Usage:**
```python
ucode_draw(panel="map")          # Draw map panel
ucode_draw(panel="hud")          # Draw HUD
ucode_draw(panel="")             # Demo panel
```

**Examples:**
- "Draw the map"
- "Show the HUD"

---

#### `ucode_sonic`
Control ambient sound and audio cues.

**Usage:**
```python
ucode_sonic(action="status")     # Check sound status
ucode_sonic(action="play", track="ambient")
ucode_sonic(action="stop")
ucode_sonic(action="list")      # Show available tracks
```

**Examples:**
- "Play ambient music"
- "Stop the music"
- "What sounds are available?"

---

#### `ucode_music`
Music playback and playlist management.

**Usage:**
```python
ucode_music(action="status")     # Show current song
ucode_music(action="play", playlist="focus")
ucode_music(action="next")
ucode_music(action="list")
```

**Examples:**
- "Play my focus playlist"
- "Skip to the next song"
- "What playlists do I have?"

---

#### `ucode_empire`
Manage multi-node wizard network.

**Usage:**
```python
ucode_empire(action="status")    # Network status
ucode_empire(action="build", node="node-1")
ucode_empire(action="expand")
ucode_empire(action="report")
```

**Examples:**
- "Show my empire status"
- "Build a new node"
- "Generate an empire report"

---

#### `ucode_destroy`
Wipe data (cache, logs, binder) - **dangerous**.

**Usage:**
```python
ucode_destroy(target="cache")               # Clear cache
ucode_destroy(target="logs")                # Clear logs
ucode_destroy(target="--all", confirm=True) # DELETE EVERYTHING
```

**Examples:**
- "Clear my cache"
- "Wipe all logs"
- ⚠️ "Delete everything (CONFIRM)"

---

#### `ucode_undo`
Undo recent actions from backup.

**Usage:**
```python
ucode_undo(steps=1)              # Undo 1 step
ucode_undo(steps=5)              # Undo 5 steps
```

**Examples:**
- "Undo the last action"
- "Undo the last 5 changes"

---

#### `ucode_print`
Format and output content with styling.

**Usage:**
```python
ucode_print(content="file.md", format="markdown")
ucode_print(content="data.json", format="json")
ucode_print(content="table.csv", format="table")
```

**Examples:**
- "Pretty-print this markdown file"
- "Display this as JSON"

---

#### `ucode_format`
Convert between data formats.

**Usage:**
```python
ucode_format(input="config.json", style="yaml")
ucode_format(input="data.yaml", style="toml")
ucode_format(input="old-format.csv", style="json")
```

**Examples:**
- "Convert this JSON to YAML"
- "Format this as CSV"

---

## Skills (Interactive Wrappers)

### /ucode-help
Get help with uDOS commands.
- List all available commands
- Get detailed help for specific commands
- Find tools by topic (system, data, navigation, etc.)

### /ucode-setup
Initialize and configure uDOS.
- Interactive setup wizard
- Configuration walkthrough
- Verify installation
- Generate credentials

### /ucode-story
Interact with narrative content.
- Read stories from your vault
- Navigate branching narratives
- Track game progress
- Resume adventures

### /ucode-logs
Access system diagnostics.
- View recent logs
- Filter by severity
- Explain errors
- Troubleshoot issues

### /ucode-dev
Developer mode and technical deep dives.
- Explore codebase
- Understand architecture
- Debug systems
- Learn implementation details

---

## Common Workflows

### Backup & Restore

```bash
> Save my state to the vault
↓ (ucode_save executed)

> Load my saved state
↓ (ucode_load executed)
```

### Project Management

```bash
> Create a new project called "feature-release"
↓ (ucode_place + ucode_binder)

> Switch to the feature-release project
↓ (ucode_place / ucode_goto)

> Show me the project status
↓ (ucode_binder status)
```

### Script Execution

```bash
> Do a dry-run of the migration
↓ (ucode_run dry_run=True)

> Execute the backup script
↓ (ucode_run)

> Schedule nightly backups
↓ (ucode_scheduler)
```

### Troubleshooting

```bash
> Check my system health
↓ (ucode_health)

> Verify my installation
↓ (ucode_verify)

> Show recent errors
↓ (ucode_logs)

> Fix any issues
↓ (ucode_repair)
```

### Content Discovery

```bash
> What stories are available?
↓ (ucode_story list)

> Tell me an adventure
↓ (ucode_story read)

> What games can I play?
↓ (ucode_play)
```

---

## Error Handling

Most tools return structured results:

```python
{
  "status": "ok" | "error" | "warning",
  "message": "Human-readable status message",
  "data": { /* tool-specific data */ }
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `vault not initialized` | Vault doesn't exist | Run `/ucode-setup` |
| `invalid path` | Path doesn't exist | Check path with `/ucode-find` |
| `permission denied` | Not authorized | Switch user with `ucode_user` |
| `command not found` | Invalid command | Get help with `ucode_help` |

---

## Advanced Usage

### Chaining Operations

```bash
> Find all backup files, load the latest one, and verify the result
↓ Vibe vibe chains: ucode_find → ucode_load → ucode_verify
```

### Conditional Execution

```bash
> If health check fails, repair, then verify
↓ Vibe orchestrates tool sequence based on results
```

### Combining Tools

```bash
> Save my state, create a backup, and schedule nightly saves
↓ ucode_save → ucode_seed → ucode_scheduler
```

---

## Configuration

### Environment Variables

Control uDOS behavior:

```bash
UDOS_ROOT=~/vibe-data          # Data directory
VAULT_ROOT=~/vibe-vault        # Vault location
UDOS_LOG_LEVEL=debug           # Log verbosity
UDOS_CACHE=1GB                 # Cache size
```

### Preferences

Configure via `ucode_config`:

```bash
> Set the vault path to /custom/vault
> Configure logging level to debug
> Set cache size to 2GB
```

---

## Quick Reference

| Task | Tool | Example |
|------|------|---------|
| Check health | `ucode_health` | "Is everything OK?" |
| Get help | `ucode_help` | "Show me all commands" |
| Save data | `ucode_save` | "Back up everything" |
| Load data | `ucode_load` | "Restore my state" |
| Run scripts | `ucode_run` | "Execute the migration" |
| Read content | `ucode_read` | "Show the guide" |
| Play games | `ucode_play` | "Start an adventure" |
| Manage projects | `ucode_place` | "Create a new project" |

---

For more information, see:
- [Roadmap](../roadmap.md)
- [Legacy Phase A/B Progress](../.compost/historic/phase-a-progress-legacy-2026-02-21.md)
- [Legacy Phase A/B Status](../.compost/historic/phase-a-status-legacy-2026-02-21.md)
- [Architecture Overview](../specs/ucode-architecture.md)
