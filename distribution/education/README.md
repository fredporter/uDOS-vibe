# uDOS v1.4.4 Educational Distribution

**Version:** v1.4.4
**Release Date:** 2026-03-31 (planned)
**Purpose:** Learn uDOS from the ground up with guided tutorials and interactive demos

---

## Quick Start

### First Time?

1. **Read:** [getting-started-cli.md](guides/getting-started-cli.md) (15 min)
2. **Run:** `bash demo-scripts/00-hello-udos.sh` (2 min)
3. **Explore:** `bash demo-scripts/01-workspace-tour.sh` (5 min)

### Want to Learn More?

- **Workspaces:** [learning-workspaces.md](guides/learning-workspaces.md)
- **Grid & Maps:** [learning-grid-and-map.md](guides/learning-grid-and-map.md)
- **Command Chaining:** [learning-commands-and-flow.md](guides/learning-commands-and-flow.md)
- **Theming:** [learning-styling-and-theming.md](guides/learning-styling-and-theming.md)
- **Advanced:** [learning-advanced-automation.md](guides/learning-advanced-automation.md)

### Need Help?

- **Command lookup:** [resources/command-reference.md](resources/command-reference.md)
- **Common errors:** [resources/error-codes.md](resources/error-codes.md)
- **Keyboard shortcuts:** [resources/keyboard-shortcuts.md](resources/keyboard-shortcuts.md)
- **Terminology:** [resources/glossary.md](resources/glossary.md)

---

## What's Inside?

### 📚 Guides (5 core curricula)

Learn uDOS with step-by-step instruction:

| Guide | Duration | Topics |
|-------|----------|--------|
| [Getting Started](guides/getting-started-cli.md) | 15 min | Run commands, get help, check health |
| [Workspaces](guides/learning-workspaces.md) | 30 min | Create, switch, organize workspaces |
| [Grid & Maps](guides/learning-grid-and-map.md) | 45 min | Spatial coordinates, grid runtime |
| [Commands & Flow](guides/learning-commands-and-flow.md) | 45 min | Chain commands, replay, automate |
| [Theming](guides/learning-styling-and-theming.md) | 30 min | Themes, colors, customization |
| [Advanced](guides/learning-advanced-automation.md) | 60 min | Rules, gameplay, plugins |

**Total estimated learning time:** ~3.5 hours

### 🎬 Demo Scripts (6 interactive examples)

Run and learn:

```bash
bash demo-scripts/00-hello-udos.sh           # 2 min  — Hello World
bash demo-scripts/01-workspace-tour.sh       # 5 min  — Interactive tour
bash demo-scripts/02-grid-explorer.sh        # 10 min — Playable grid
bash demo-scripts/03-command-matrix.sh       # 15 min — All commands
bash demo-scripts/04-theme-viewer.sh         # 10 min — Theme gallery
bash demo-scripts/05-gameplay-replay.sh      # 20 min — Game replay
```

**Total interactive time:** ~60 minutes

### 📖 Examples & Resources

- Sample workspace layouts
- Real command transcripts
- Quick reference cards
- Error solutions
- Glossary

---

## How to Use This Pack

### Self-Paced Learning

1. Start with guide 1 (15 min)
2. Try demo-script 00 and 01 (7 min)
3. Move to guide 2 (30 min)
4. Continue with remaining guides at your pace
5. Use resource cards as needed

### Group Learning

- Guides work for study groups (discuss concepts)
- Demo scripts great for classroom/workshop demos
- Resources can be printed or shared

### Reference Use

- Keep command reference handy while using uDOS
- Refer to error codes when you get stuck
- Use glossary to learn terminology

---

## Learning Objectives

By the end of this pack, you'll be able to:

- [ ] Launch uDOS and run basic commands
- [ ] Create and switch between workspaces
- [ ] Understand vault structure and binders
- [ ] Navigate spatial grids and maps
- [ ] Chain commands for complex workflows
- [ ] Understand game state and progression
- [ ] Customize themes and appearance
- [ ] Write automation rules
- [ ] Troubleshoot common errors

---

## System Requirements

- **OS:** Linux, macOS, or WSL (Windows)
- **Interpreter:** Bash shell
- **uDOS:** v1.4.4 or later installed (see [INSTALLATION.md](../../INSTALLATION.md))
- **Editor:** Any text editor (VS Code recommended)

---

## Contents Overview

```
education/
├── README.md                     # This file
├── MANIFEST.md                  # Detailed structure & content plan
├── guides/
│   ├── getting-started-cli.md
│   ├── learning-workspaces.md
│   ├── learning-grid-and-map.md
│   ├── learning-commands-and-flow.md
│   ├── learning-styling-and-theming.md
│   └── learning-advanced-automation.md
├── demo-scripts/
│   ├── README.md
│   ├── 00-hello-udos.sh
│   ├── 01-workspace-tour.sh
│   ├── 02-grid-explorer.sh
│   ├── 03-command-matrix.sh
│   ├── 04-theme-viewer.sh
│   └── 05-gameplay-replay.sh
├── examples/
│   ├── workspace-layout-tutorial.md
│   ├── binder-content-examples/
│   └── command-transcripts.txt
├── resources/
│   ├── command-reference.md
│   ├── error-codes.md
│   ├── keyboard-shortcuts.md
│   ├── ascii-art-reference.md
│   └── glossary.md
└── video-notes/ (optional)
    ├── episode-01-getting-started.md
    └── episode-02-advanced-workflows.md
```

---

## FAQ

**Q: Do I need experience with the command line?**
A: No! This pack teaches you from the ground up. Basic computer skills are enough.

**Q: How long will it take to learn?**
A: 3-4 hours for core concepts; ongoing learning as you use uDOS.

**Q: Can I use this offline?**
A: Yes! All guides and demos work offline.

**Q: Where's the official documentation?**
A: This is educational. Full reference docs are in [../../docs](../../docs).

**Q: How do I report errors in the guides?**
A: File an issue on GitHub or contact the community.

**Q: Can I share these guides?**
A: Yes! They're part of uDOS (same license).

**Q: Are there videos?**
A: Transcripts are in `video-notes/` if videos are available.

---

## Suggested Learning Path

### Path A: Quick Start (1 hour)

→ Gets you productive quickly, minimal depth

```
getting-started-cli.md (15 min)
  ↓
demo-scripts/00-01 (7 min)
  ↓
learning-workspaces.md (30 min)
  ↓
Try it yourself: Create a workspace + add a document
```

### Path B: Comprehensive (3.5 hours)

→ Deep understanding of all features

```
All 6 guides in order (3 hours)
  ↓
Demo scripts in order (1 hour)
  ↓
Practice exercises (30 min)
  ↓
Review resource cards as needed
```

### Path C: Specialized (varies)

→ Focus on what you need

```
Choose guides by interest:
  - Workspace organized? → workspaces + grid
  - Want automation? → commands + advanced
  - Love design? → theming
  - Gameplay? → grid + advanced
```

---

## Learn by Doing

Each guide includes:

- **Concepts** — Key ideas explained
- **Examples** — Real command examples
- **Practice** — Hands-on exercises
- **Troubleshooting** — Common issues + fixes
- **Next Steps** — What to learn next

---

## Contributing

Found an error? Want to improve?

1. Fork the repo
2. Edit the guide
3. Submit a pull request

See [../../CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

---

## License

Same as uDOS. See [../../LICENSE.txt](../../LICENSE.txt).

---

## Credits

Created for uDOS v1.4.4 as part of the educational distribution initiative.

---

**Ready to learn?** Start with [guides/getting-started-cli.md](guides/getting-started-cli.md) →

_Last updated: 2026-03-31_
_Version: 1.0.0_
