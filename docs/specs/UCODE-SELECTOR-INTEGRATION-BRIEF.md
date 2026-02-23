# Selector Integration Brief for vibe-cli Addon Commands

**Objective**: Define a standardized approach for integrating interactive selectors (file pickers, menus, and multi-select prompts) into `vibe-cli` addon commands (`/ucode`), while preserving scriptable shell-first behavior for the ucode command set.

---

## 1. Overview

This brief defines implementation guidance for interactive selectors in `/ucode` commands.
The design target is a consistent, keyboard-driven terminal experience that aligns with `vibe-cli`, without breaking automation or non-interactive shell execution.

---

## 2. Core Requirements

- Compatibility: tools must run on Linux, macOS, and Windows.
- TUI alignment: selector UX should match `vibe-cli` terminal conventions.
- Zero cost: use only free/open-source tools.
- Scriptable fallbacks: every interactive path must have non-interactive CLI arguments.

---

## 3. Recommended Tools

### A. File Pickers

| Tool | Language | Features | Example Use Case |
|---|---|---|---|
| [`fzf`](https://github.com/junegunn/fzf) | Shell | Fuzzy search, preview, multi-select, fast integration with `find`/`fd`. | Selecting files/directories. |
| [`pick`](https://github.com/wong2/pick) | Python | Simple, cross-platform, single/multi-select. | Python-based file selection. |
| [`fd`](https://github.com/sharkdp/fd) + `fzf` | Shell | Fast recursive search plus fuzzy filtering. | Recursive file search + selection. |

`fzf` is the default match for `vibe-cli` style: minimal, keyboard-first, composable.

### B. Menu/Option Selectors

| Tool | Language | Features | Example Use Case |
|---|---|---|---|
| [`InquirerPy`](https://github.com/kazhala/InquirerPy) | Python | Rich prompts: lists, checkboxes, confirmations, themes. | Multi-step workflows. |
| Bash `select` | Shell | Built-in simple menus. | Basic option selection. |
| [`gum`](https://github.com/charmbracelet/gum) | Shell | Modern prompts for choose/input/confirm, cross-platform. | User-friendly CLI menus. |

`gum` is preferred for polished shell-native menus.

### C. Checkboxes/Multi-Select

| Tool | Language | Features | Example Use Case |
|---|---|---|---|
| `InquirerPy` | Python | Checkbox prompts for multi-select. | Multiple files/actions. |
| `fzf -m` | Shell | Fuzzy multi-select. | Batch file operations. |
| `gum choose --multi` | Shell | Simple multi-select menus. | Selecting multiple options. |

Compatibility note:
- In this repository's Python 3.12 runtime, `PyInquirer` is legacy and not part of the supported stack.
- `pick` is the default supported Python selector dependency.
- `InquirerPy` is optional for richer prompts when explicitly installed.

---

## 4. Integration Guidelines

### A. Shell-Based `/ucode` Commands

Use `fd` + `fzf` for file picking:

```bash
selected_files="$(fd --type f | fzf --multi --preview 'bat --color=always {}')"
printf 'Selected: %s\n' "$selected_files"
```

Use `gum` for menus:

```bash
choice="$(gum choose "Parse" "Format" "Exit")"
printf 'You chose: %s\n' "$choice"
```

### B. Python-Based `/ucode` Commands

Use `InquirerPy` for rich prompts:

```python
from InquirerPy import inquirer

questions = [
    {
        "type": "checkbox",
        "name": "files",
        "message": "Select files to process:",
        "choices": ["file1.txt", "file2.txt", "file3.txt"],
    }
]
answers = inquirer.checkbox(
    message="Select files to process:",
    choices=["file1.txt", "file2.txt", "file3.txt"],
).execute()
print(f"Selected: {answers}")
```

Use `pick` for simple selection:

```python
from pick import pick

options = ["Parse", "Format", "Exit"]
selected, _ = pick(options, "Choose an action:")
print(f"You selected: {selected}")
```

---

## 5. Fallback for Non-Interactive Use

Every interactive command path must support explicit non-interactive flags:

```bash
ucode parse --files "file1.txt file2.txt"
```

---

## 6. Visual Consistency with vibe-cli

- Colors: align tool theming with `vibe-cli` style (`gum` theme options, `fzf --color`).
- Keybindings: preserve expected terminal controls (`Ctrl+C` exit, `Enter` select).
- Preview panes: use `fzf --preview` (and equivalent where available) for file context.

---

## 7. Example Workflows

### A. File Picker Workflow (Shell)

```bash
files="$(fd --type f | fzf --multi --preview 'head -n 10 {}')"
printf '[ucode] Processing files: %s\n' "$files"
```

### B. Menu-Driven Workflow (Python)

```python
from PyInquirer import prompt

questions = [
    {
        "type": "list",
        "name": "action",
        "message": "What would you like to do?",
        "choices": ["Parse", "Format", "Exit"],
    }
]
answers = prompt(questions)
print(f"Executing: {answers['action']}")
```

---

## 8. Summary Table

| Use Case | Recommended Tool | Language | Notes |
|---|---|---|---|
| File picker | `fzf` + `fd` | Shell | Fast, fuzzy, previewable. |
| Menu selector | `gum` | Shell | Modern, themable, cross-platform. |
| Checkbox/multi-select | `pick` (default), `InquirerPy` (optional) | Python | `pick` is the repo default on Python 3.12. |
| Simple menu | Bash `select` | Shell | Built-in, no dependencies. |

---

## 9. Implementation Checklist

1. Detect interactive environment (`$TERM`, TTY checks such as `sys.stdout.isatty()`).
2. Default to recommended tools (`fzf`/`gum` in shell, `pick` in Python).
3. Provide non-interactive fallbacks (for example, `--file` or `--files`).
4. Match `vibe-cli` keybindings/colors.
5. Document interactive and scripted usage in command help output.

---

## 10. Example Full `/ucode` Command (Python)

```python
#!/usr/bin/env python3
import sys

from InquirerPy import inquirer


def main() -> None:
    if not sys.stdout.isatty():
        print("Non-interactive mode. Use --file <file>.")
        return

    action = inquirer.select(
        message="Select an action:",
        choices=["Parse", "Format", "Exit"],
    ).execute()
    print(f"[ucode] Executing: {action}")


if __name__ == "__main__":
    main()
```

---

This standard keeps `/ucode` commands interactive and user-friendly while preserving deterministic shell automation paths required by the ucode command set.
