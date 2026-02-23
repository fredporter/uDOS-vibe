# Getting Started with uDOS CLI

**Duration:** 15 minutes
**Level:** Beginner
**Prerequisites:** None — we'll start from scratch

---

## Learning Objectives

By the end of this guide, you'll be able to:

- [ ] Launch uDOS in your terminal
- [ ] Run your first command
- [ ] Understand command output
- [ ] Get help for any command
- [ ] Check system health

---

## What is uDOS?

uDOS is a **command-line companion** for organizing your knowledge and creative work.

Think of it as:
- 📚 **Knowledge organizer** — Manage documents in workspaces
- 🎮 **Game-like interface** — Explore with spatial coordinates
- 🧩 **Modular framework** — Extend with plugins
- 📝 **Markdown-native** — Everything is markdown

**Key concept:** uDOS runs locally (on your machine), respects your privacy, and works offline.

### Example: What uDOS Does

```
Your creative workspace:
    @vault/          ← Main workspace
    ├── projects/    ← Document collections
    ├── places/      ← Spatial game world
    ├── logs/        ← Run records
    └── inbox/       ← Quick capture

uDOS helps you:
  • Navigate between workspaces
  • Create and edit documents
  • Visualize with ASCII art
  • Play games with persistent state
  • Automate workflows via rules
```

---

## Part 1: Your First Command (5 minutes)

### Step 1: Open Terminal

Open a terminal in your OS:

**macOS:**
```
Press ⌘ Cmd + Space, type "terminal", press Enter
```

**Linux:**
```
Ctrl + Alt + T  (most distros)
or open your favorite terminal
```

**Windows (WSL):**
```
Search for "Ubuntu" or your WSL distro in Start menu
```

**Expected:** You'll see a prompt like `$ ` or `user@computer:~$`

### Step 2: Run Your First Command

Type this and press Enter:

```bash
ucode HELP
```

**What happened?**

uDOS printed a welcome message with a list of commands:

```
=== uDOS Command Reference ===

HELP     — Show help (you just ran this!)
HEALTH   — Check system status
VERIFY   — Validate documents
PLACE    — Switch workspace
BINDER   — List documents
DRAW     — Render TUI widgets
RUN      — Chain commands
PLAY     — Game commands
RULE     — Automation rules
LIBRARY  — Package manager

Use: ucode <COMMAND> --help  for details
```

**Success!** You just ran your first uDOS command. 🎉

### Step 3: Understanding Command Structure

```
ucode    HELP    --verbose
 ↓       ↓         ↓
tool   command   flag
```

- **`ucode`** — The uDOS command-line tool
- **`HELP`** — The command name (usually uppercase)
- **`--verbose`** — Optional flag (usually `--flag-name`)

### Step 4: Get Help for a Specific Command

Type:

```bash
ucode HELP HEALTH
```

**Output:**

```
HEALTH — Check system status

SYNOPSIS
    ucode HEALTH [OPTIONS]

DESCRIPTION
    Checks the health of your uDOS installation and services.

OPTIONS
    --verbose    Show detailed information
    --check-services  Check connected services (Wizard)

EXAMPLES
    ucode HEALTH              — Quick status check
    ucode HEALTH --verbose    — Detailed report
    ucode HEALTH --check-services  — Include Wizard services
```

**Tip:** You can get help for **any** command by running:
```bash
ucode <COMMAND> --help
```

---

## Part 2: Check Your System (5 minutes)

### Step 1: Run Health Check

Type:

```bash
ucode HEALTH
```

**Example output:**

```
✓ uDOS Core v1.4.4    — RUNNING
✓ Vault location      — /Users/you/.udos/vault
✓ Workspace @vault    — READY (42 documents)
✓ Python runtime      — 3.11.8 (stdlib-only)
✓ Cache               — VALID (updated 30s ago)

Status: All systems operational
```

**What you see:**

- ✓ means working
- ✗ means there's an issue
- Each line shows one component

### Step 2: Verbose Output

For more details, try:

```bash
ucode HEALTH --verbose
```

**Example output:**

```
=== uDOS System Health Report ===

Core Runtime
  Version:       v1.4.4
  Status:        RUNNING
  Uptime:        3m 42s
  Memory:        24.3 MB

Vault
  Location:      /Users/you/.udos/vault
  Type:          Local
  Size:          1.2 MB
  Documents:     42
  Last sync:     30s ago

Workspaces
  @vault:        READY (42 docs)
  @dev:          READY (8 docs)
  @archive:      READY (156 docs)

Python Engine
  Version:       3.11.8
  Venv:          System (stdlib-only)
  Modules:       Core, Services, Commands

Services
  Wizard:        NOT RUNNING (optional)
  Cache:         VALID
  Logger:        ACTIVE

Overall Status: PASS ✓
```

This tells you everything is working correctly.

### Step 3: What if Something's Wrong?

If you see ✗, here are some tips:

| Problem | Solution |
|---------|----------|
| "Vault not found" | Run `ucode PLACE --list` to see workspaces |
| "Python error" | Check you're using Python 3.8+ (run `python3 --version`) |
| "Permission denied" | Make sure vault folder is readable (ask system admin) |
| "Wizard services down" | Optional — uDOS works offline without Wizard |

**Getting more help?** Run:
```bash
ucode HEALTH --debug  # Show detailed error info
```

---

## Part 3: Understanding Workspaces (3 minutes)

### Key Concept: What's a Workspace?

A **workspace** (written as `@name`) is a folder that holds your documents.

Think of it like:
- **@vault** = Main folder for everything
- **@dev** = Separate folder for development docs
- **@archive** = Folder for old, archived stuff

### Step 1: List Your Workspaces

Type:

```bash
ucode PLACE --list
```

**Output:**

```
=== Available Workspaces ===

@vault        (current)  42 documents
@dev                     8 documents
@archive                 156 documents

Use: ucode PLACE @NAME  to switch
```

- **(current)** shows your current workspace
- Numbers show how many documents in each

### Step 2: Switch a Workspace

Try switching to @dev:

```bash
ucode PLACE @dev
```

**Output:**

```
✓ Switched to @dev
  - 8 documents loaded
  - Cache invalidated and refreshed
  - Current workspace: @dev
```

Now you're in the `@dev` workspace!

### Step 3: Check What's in Your Workspace

Type:

```bash
ucode BINDER --list
```

**Output:**

```
=== Documents in @dev ===

1. README.md
2. setup-notes.md
3. ideas-backlog.md
4. meeting-2026-02-20.md
5. experiment-01.md
6. experiment-02.md
7. experiment-03.md
8. learning-log.md

Use: ucode DRAW PREVIEW <filename>  for preview
```

These are the markdown files in your workspace.

### Step 4: Switch Back

Try switching back to your main workspace:

```bash
ucode PLACE @vault
```

**Congratulations!** You've now navigated between workspaces. 🚀

---

## Part 4: Help Anytime (Ongoing Reference)

### The Three Ways to Get Help

#### 1. Command Help (`--help`)

```bash
ucode PLACE --help        # Help for PLACE command
ucode DRAW --help         # Help for DRAW command
ucode RUN --help          # Help for RUN command
```

#### 2. General Help (`HELP <COMMAND>`)

```bash
ucode HELP PLACE          # Tell me about PLACE
ucode HELP DRAW           # Tell me about DRAW
```

#### 3. Full Reference (`HELP`)

```bash
ucode HELP                # Show all commands
```

**Pro tip:** Stuck? Try `--help` first. It's usually faster than searching.

---

## Common First Commands

Here are commands most people run first:

### 1. Check Status (Always Safe)
```bash
ucode HEALTH
```

### 2. Explore Workspaces
```bash
ucode PLACE --list
ucode PLACE @vault
ucode BINDER --list
```

### 3. Get Help
```bash
ucode HELP
ucode HELP PLACE
```

### 4. Verify Everything Works
```bash
ucode VERIFY
```

---

## Practice Exercises

Try these to reinforce what you learned:

### Exercise 1: Navigate Workspaces
```bash
# List all workspaces
ucode PLACE --list

# Switch to @dev
ucode PLACE @dev

# Check status
ucode HEALTH

# View documents
ucode BINDER --list

# Switch back
ucode PLACE @vault
```

**Expected:** No errors; you successfully navigate between workspaces.

### Exercise 2: Get Help
```bash
# Get general help
ucode HELP

# Get help for PLACE
ucode HELP PLACE

# Get help via flag
ucode PLACE --help

# Get quick status
ucode HEALTH
```

**Expected:** You can see help text for every command.

### Exercise 3: Explore
```bash
# Long manual for HELP
ucode HELP --verbose

# Detailed health report
ucode HEALTH --verbose

# List workspaces with details
ucode PLACE --list --verbose
```

**Expected:** You understand how to get more detailed information.

---

## Troubleshooting

### Problem: "Command not found: ucode"

**Cause:** uDOS isn't installed or not in your PATH

**Solution:**
```bash
# Check if installed
which ucode

# If not found, reinstall (see INSTALLATION.md)
bash install.sh
```

### Problem: "Permission denied"

**Cause:** Vault folder isn't readable

**Solution:**
```bash
# Check permissions
ls -la ~/.udos/vault

# Fix if needed (ask system admin)
chmod 755 ~/.udos/vault
```

### Problem: "Python error" or "Module not found"

**Cause:** Wrong Python version or environment

**Solution:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check uDOS version
ucode HELP | head
```

### Problem: "Workspace not found"

**Cause:** Typed workspace name wrong, or missing @

**Solution:**
```bash
# Check available workspaces
ucode PLACE --list

# Make sure to use @ prefix
ucode PLACE @vault    # Correct
ucode PLACE vault     # Wrong
```

---

## What's Next?

Now that you can run commands, try these next steps:

1. **[Learning Workspaces](learning-workspaces.md)** (30 min)
   - Create your own workspace
   - Understand vault structure
   - Best practices for organization

2. **Try a Demo Script**
   ```bash
   bash ../demo-scripts/00-hello-udos.sh       # 2 min
   bash ../demo-scripts/01-workspace-tour.sh   # 5 min
   ```

3. **Explore More Commands**
   ```bash
   ucode HELP          # See all commands
   ucode HELP PLACE    # Learn about PLACE
   ucode HELP BINDER   # Learn about BINDER
   ```

---

## Summary: What You Learned

✓ How to launch uDOS using `ucode`
✓ How to run commands
✓ How to get help
✓ How to check system health
✓ How to navigate workspaces
✓ How to explore documents

---

## Keyboard Tips

Here are some terminal shortcuts to make life easier:

| Key | What It Does |
|-----|--------------|
| `↑` (up arrow) | Previous command |
| `↓` (down arrow) | Next command |
| `Tab` | Auto-complete command |
| `Ctrl+C` | Cancel running command |
| `Ctrl+L` | Clear screen |
| `Ctrl+U` | Clear current line |

---

## Still Stuck?

- Run `ucode HELP` for full command list
- Check the [error codes](../resources/error-codes.md) guide
- See [FAQ](../README.md#faq) in main README

---

## Next Lesson: Learning Workspaces

Ready to create your own workspace and organize documents?

→ [Learning Workspaces](learning-workspaces.md)

---

**Estimated time to complete:** 15 minutes ✓
**Difficulty:** Beginner
**Practice time:** 10 minutes additional

_Last updated: 2026-03-31_
