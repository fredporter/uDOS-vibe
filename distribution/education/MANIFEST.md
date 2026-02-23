# Educational Distribution Manifest — v1.4.4

**Status:** Planning
**Target:** Generation during v1.4.4 Phase 2
**Purpose:** Curated learning materials for community education and self-paced learning

---

## Structure

```
distribution/education/
├── MANIFEST.md                          # This file
├── README.md                            # Getting started guide
├── guides/
│   ├── getting-started-cli.md          # Learn basic commands
│   ├── learning-workspaces.md          # Learn @workspace system
│   ├── learning-grid-and-map.md        # Learn spatial/grid runtime
│   ├── learning-commands-and-flow.md   # Command chaining, replay
│   ├── learning-styling-and-theming.md # Theme packs, TUI customization
│   └── learning-advanced-automation.md # Rules, gameplay, extensions
│
├── demo-scripts/
│   ├── 00-hello-udos.sh               # Minimal TUI Hello World
│   ├── 01-workspace-tour.sh           # Interactive @workspace navigation
│   ├── 02-grid-explorer.sh            # Spatial grid demo
│   ├── 03-command-matrix.sh           # Exhaustive command invocation
│   ├── 04-theme-viewer.sh             # Theme pack gallery
│   ├── 05-gameplay-replay.sh          # Recorded gameplay replay
│   └── README.md                       # Demo script reference
│
├── examples/
│   ├── workspace-layout-tutorial.md    # Example workspace structure
│   ├── binder-content-examples/        # Example markdown content
│   ├── command-transcripts.txt         # Real command sessions
│   └── gameplay-saves/                 # Sample game saves (optional)
│
├── video-notes/                        # Transcripts/notes for video tutorials
│   ├── episode-01-getting-started.md
│   └── episode-02-advanced-workflows.md
│
└── resources/
    ├── command-reference.md            # Quick command lookup
    ├── error-codes.md                  # Common errors + solutions
    ├── keyboard-shortcuts.md           # Keyboard reference
    ├── ascii-art-reference.md          # TUI rendering reference
    └── glossary.md                     # Terminology guide
```

---

## Guide Content

### getting-started-cli.md

**Duration:** 15 minutes
**Target:** Complete beginners
**Topics:**
- What is uDOS?
- Running your first command (HELP)
- Understanding command output
- Getting command help (HELP command, --help flags)
- Health checks (HEALTH)
- Basic navigation (PLACE)

### learning-workspaces.md

**Duration:** 30 minutes
**Target:** Users learning workspace system
**Topics:**
- Workspace concept (@workspace syntax)
- Creating workspaces
- Switching between workspaces
- Workspace structure (vault layout)
- Benefits of multi-workspace approach
- Binder organization within workspaces

### learning-grid-and-map.md

**Duration:** 45 minutes
**Target:** Advanced users, game players
**Topics:**
- Spatial coordinate system (LocId, PlaceRef)
- Grid runtime internals
- Viewport calculations
- Map rendering (DRAW, PLAY LENS)
- Place connections and adjacency
- Basic pathfinding concepts

### learning-commands-and-flow.md

**Duration:** 45 minutes
**Target:** Workflow automation users
**Topics:**
- Command chaining (RUN command)
- State persistence
- Replay and deterministic execution
- Error recovery
- Scripting with uCODE
- Integration with external tools

### learning-styling-and-theming.md

**Duration:** 30 minutes
**Target:** Designers, customization enthusiasts
**Topics:**
- Theme pack structure
- Available color schemes
- Custom theme creation
- TUI widget customization
- Applying themes globally
- Creating personal themes

### learning-advanced-automation.md

**Duration:** 60 minutes
**Target:** Advanced users, power users
**Topics:**
- RULE command (IF/THEN automation)
- Gameplay state machines
- Integration with Wizard services
- Plugin development concepts
- Custom command creation
- Extending Core via services

---

## Demo Script Details

### 00-hello-udos.sh

**Duration:** 2 minutes
**Output:** Single TUI render
**Code:**
```bash
#!/bin/bash
# Minimal uDOS Hello World demo
printf 'DRAW BOX --text="Hello, uDOS v1.4!\n' | ucode
```

### 01-workspace-tour.sh

**Duration:** 5 minutes
**Output:** Interactive workspace navigation
**Features:**
- Lists available workspaces
- Switches between them interactively
- Shows workspace contents

### 02-grid-explorer.sh

**Duration:** 10 minutes
**Output:** Playable spatial grid demo
**Features:**
- Renders a 30x20 grid
- Allows arrow-key movement
- Shows place names and connections
- Explains game mechanics

### 03-command-matrix.sh

**Duration:** 15 minutes
**Output:** Matrix of all command invocations
**Features:**
- Runs all commands with --help
- Times each command
- Shows output for each
- Reports coverage

### 04-theme-viewer.sh

**Duration:** 10 minutes
**Output:** Gallery of all available themes
**Features:**
- Renders same widget in each theme
- Shows color palettes
- Allows switching themes

### 05-gameplay-replay.sh

**Duration:** 20 minutes
**Output:** Recorded gameplay session
**Features:**
- Loads a saved game state
- Replays recorded actions
- Shows game state changes
- Interactive pause/resume

---

## Examples

### workspace-layout-tutorial.md

Shows canonical template for workspace structure:

```
@vault/
├── 00_QUICKSTART/
│   └── Welcome to Your Vault.md
├── 01_SYSTEM/
│   ├── Configuration.md
│   └── Status.md
├── 02_ARCHIVE/
├── 03_INBOX/
├── 04_PROJECTS/
├── 05_PLACES/
│   └── L101-CC01-Tavern.md
├── 06_RUNS/
│   └── 2026-02-20-Gameplay-Log.md
└── 07_LOGS/
    └── system.log
```

### binder-content-examples/

Sample markdown files showing:
- Proper frontmatter (title, location_id, tags)
- Heading hierarchy
- Internal links (@workspace, @binder syntax)
- Code blocks with syntax highlighting
- Tables and lists
- Embedded media references

### command-transcripts.txt

Real command session showing:
```
$ ucode
> HELP
> PLACE --list
> PLACE @dev
> BINDER --list
> VERIFY
> HEALTH
```

---

## Resources

### command-reference.md

Quick lookup table:

| Command | Purpose | Quick Example |
|---------|---------|---------------|
| HELP | Show help | HELP PLACE |
| HEALTH | Check system status | HEALTH --verbose |
| VERIFY | Validate documents | VERIFY --check |
| PLACE | Switch workspace | PLACE @dev |
| BINDER | List documents | BINDER --list |
| DRAW | Render widgets | DRAW BOX |
| RUN | Chain commands | RUN HELP; HEALTH |
| PLAY | Game system | PLAY --status |
| RULE | Automation | RULE --evaluate |
| LIBRARY | Package manager | LIBRARY sync |

### error-codes.md

Common errors with solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| ERR_WORKSPACE_NOT_FOUND | Workspace doesn't exist | PLACE --list (list available) |
| ERR_COMMAND_INVALID_ARG | Missing required argument | Check --help for syntax |
| ERR_PARSER_SYNTAX | Malformed markdown | Check for unclosed code blocks |

### keyboard-shortcuts.md

Reference for uCODE and TUI shortcuts:

| Key | Action |
|-----|--------|
| Tab | Auto-complete command |
| Ctrl+C | Cancel command |
| Ctrl+L | Clear screen |
| ↑/↓ | Command history |

### ascii-art-reference.md

Visual reference for TUI elements:

- Box drawing: `┌─┐ ├─┤ └─┘`
- List items: `• ◦ ▪`
- Arrows: `→ ↓ ← ↑`
- Progress: `⠄ ⠂ ⠁ █ ░`
- Grid: `╔═╦╗ ╠═╬╣ ╚═╩╝`

### glossary.md

Key terms defined:

- **@workspace:** Logical workspace container (`@vault`, `@dev`, etc.)
- **Binder:** Document collection within workspace
- **LocId:** Spatial location identifier (`L###-CC##`)
- **PlaceRef:** Reference to a place entity
- **Vault:** Structured document tree
- **Gameplay:** Game state and progression system
- **Lens:** Alternative view onto world state (2D map, 3D view, etc.)

---

## Deployment & Distribution

### v1.4.4 Phase 2 Deliverables

- [ ] All guides written (Markdown format, 10k-15k total words)
- [ ] All demo scripts created and tested
- [ ] Example files and transcripts collected
- [ ] Resources completed (reference cards, glossary)
- [ ] Video transcripts added (if video tutorials produced)

### Packaging

```bash
# Create distribution tarball
tar czf uDOS-v1.4.4-education-pack.tar.gz distribution/education/

# Or distribute via:
# - GitHub releases
# - ReadTheDocs hosting
# - Official documentation site
# - Community wiki
```

### Markup & Accessibility

- [ ] All `.md` files use semantic markdown (headings, lists, tables)
- [ ] All code blocks include language hint
- [ ] All scripts are executable and tested
- [ ] All guide durations are realistic
- [ ] All guides reference next steps

---

## Success Criteria

- [ ] 5 core guides completed (75+ pages)
- [ ] 6 demo scripts all executable and passing
- [ ] 5 resource reference cards complete
- [ ] All guides include learning objectives
- [ ] All guides include practice exercises
- [ ] All guides include troubleshooting sections
- [ ] Video transcripts available (if applicable)
- [ ] Community feedback incorporated

---

## Timeline

**Target:** 2026-03-15 to 2026-03-31

- **03-15 to 03-20:** Write 5 core guides
- **03-20 to 03-25:** Create 6 demo scripts; test
- **03-25 to 03-28:** Create resource cards; review
- **03-28 to 03-31:** Final polish; package for distribution

---

## Maintenance

Post v1.4.4:

- Quarterly reviews for accuracy
- Community feedback incorporation
- Update when command interfaces change
- Archive old versions when major revisions occur

---

## References

- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution)
- [core/README.md](../../core/README.md)
- [Getting Started](../../QUICKSTART.md)
