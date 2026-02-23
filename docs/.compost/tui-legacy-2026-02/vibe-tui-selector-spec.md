# **Selector Integration Brief for vibe-cli Addon Commands**
**Objective**: Define a standardized approach for integrating interactive selectors (file pickers, menus, etc.) into **vibe-cli addon commands** (`/ucli`), ensuring compatibility with vibe-cli’s existing TUI and leveraging free, open-source tools.

---

## **1. Overview**
This brief outlines how to implement **interactive selectors** (file pickers, menus, checkboxes, etc.) in `/ucli` commands, using tools that align with vibe-cli’s TUI style and are freely available. The goal is to provide a **consistent, user-friendly experience** for both interactive and scripted workflows.

---

## **2. Core Requirements**
- **Compatibility**: Tools must work across **Linux/macOS/Windows**.
- **TUI Alignment**: Selectors should visually match vibe-cli’s existing terminal UI (e.g., minimalist, keyboard-driven).
- **Zero Cost**: Only free/open-source tools.
- **Scriptable Fallbacks**: Non-interactive alternatives for automation (e.g., `--file` arguments).

---

## **3. Recommended Tools**
### **A. File Pickers**
| Tool          | Language   | Features                                                                 | Example Use Case                     |
|---------------|------------|--------------------------------------------------------------------------|---------------------------------------|
| [`fzf`](https://github.com/junegunn/fzf) | Shell      | Fuzzy search, preview, multi-select, fast, integrates with `find`/`fd`. | Selecting files/directories.         |
| [`pick`](https://github.com/wong2/pick)  | Python     | Simple, cross-platform, single/multi-select.                           | Python-based file selection.         |
| [`fd`](https://github.com/sharkdp/fd) + `fzf` | Shell | Faster `find` alternative + fuzzy filtering.                          | Recursive file search + selection.   |

**Vibe-cli TUI Match**: `fzf`’s minimalist, keyboard-driven UI aligns well with vibe-cli’s style.

---

### **B. Menu/Option Selectors**
| Tool                  | Language   | Features                                                                 | Example Use Case                     |
|-----------------------|------------|--------------------------------------------------------------------------|---------------------------------------|
| [`PyInquirer`](https://github.com/CITGuru/PyInquirer) | Python | Rich prompts (lists, checkboxes, confirmations), themable.               | Multi-step command workflows.        |
| Bash `select`         | Shell      | Built-in, simple menus.                                                  | Basic option selection.               |
| [`gum`](https://github.com/charmbracelet/gum) | Shell | Modern, stylish prompts (lists, inputs, confirms), cross-platform.       | User-friendly CLI menus.              |

**Vibe-cli TUI Match**: `gum` provides a polished, modern TUI similar to vibe-cli’s aesthetic.

---

### **C. Checkboxes/Multi-Select**
| Tool                  | Language   | Features                                                                 | Example Use Case                     |
|-----------------------|------------|--------------------------------------------------------------------------|---------------------------------------|
| `PyInquirer`          | Python     | Checkbox prompts for multi-select.                                      | Selecting multiple files/actions.    |
| `fzf` (with `-m`)     | Shell      | Multi-select with fuzzy filtering.                                      | Batch file operations.               |
| `gum choose --multi`  | Shell      | Simple multi-select menus.                                              | Choosing multiple options.            |

---

## **4. Integration Guidelines**
### **A. For Shell-Based `/ucli` Commands**
- Use **`fzf` + `fd`** for file picking:
  ```bash
  # Example: File picker in a shell script
  selected_files=$(fd --type f | fzf --multi --preview "bat --color=always {}")
  echo "Selected: $selected_files"
  ```
- Use **`gum`** for menus:
  ```bash
  # Example: Menu selector
  choice=$(gum choose "Parse" "Format" "Exit")
  echo "You chose: $choice"
  ```

### **B. For Python-Based `/ucli` Commands**
- Use **`PyInquirer`** for rich prompts:
  ```python
  from PyInquirer import prompt
  questions = [
      {
          "type": "checkbox",
          "name": "files",
          "message": "Select files to process:",
          "choices": ["file1.txt", "file2.txt", "file3.txt"]
      }
  ]
  answers = prompt(questions)
  print(f"Selected: {answers['files']}")
  ```
- Use **`pick`** for simple selections:
  ```python
  from pick import pick
  options = ["Parse", "Format", "Exit"]
  selected, _ = pick(options, "Choose an action:")
  print(f"You selected: {selected}")
  ```

---

## **5. Fallback for Non-Interactive Use**
Always support **non-interactive arguments** for scripting:
```bash
# Example: Non-interactive file selection
ucli parse --files "file1.txt file2.txt"
```

---

## **6. Visual Consistency with vibe-cli TUI**
- **Colors**: Use vibe-cli’s color scheme (e.g., `gum`’s `--theme` or `fzf`’s `--color`).
- **Keybindings**: Align with vibe-cli (e.g., `Ctrl+C` to exit, `Enter` to select).
- **Preview Panes**: Use `fzf`’s `--preview` or `gum`’s previews for file content.

---

## **7. Example Workflows**
### **A. File Picker Workflow**
```bash
# Shell script example
files=$(fd --type f | fzf --multi --preview "head -n 10 {}")
[ucli] Processing files: $files
```

### **B. Menu-Driven Workflow**
```python
# Python script example
from PyInquirer import prompt
questions = [
    {
        "type": "list",
        "name": "action",
        "message": "What would you like to do?",
        "choices": ["Parse", "Format", "Exit"]
    }
]
answers = prompt(questions)
print(f"Executing: {answers['action']}")
```

---

## **8. Summary Table: Tool Recommendations**


Selector Tools for /ucli Commands


| Use Case               | Recommended Tool       | Language   | Notes                                  |
|------------------------|------------------------|------------|----------------------------------------|
| File Picker            | `fzf` + `fd`          | Shell      | Fast, fuzzy, previewable.              |
| Menu Selector          | `gum`                 | Shell      | Modern, themable, cross-platform.      |
| Checkbox/Multi-Select  | `PyInquirer`          | Python     | Rich, scriptable, customizable.        |
| Simple Menu            | Bash `select`         | Shell      | Built-in, no dependencies.             |

---

## **9. Implementation Checklist**
1. **Detect Environment**: Check if the terminal supports interactivity (e.g., `$TERM`, `sys.stdout.isatty()` in Python).
2. **Use Recommended Tools**: Default to `fzf`/`gum` (shell) or `PyInquirer` (Python).
3. **Provide Fallbacks**: Always allow non-interactive arguments (e.g., `--file`).
4. **Match vibe-cli’s TUI**: Use consistent colors/keybindings.
5. **Document**: Clearly document interactive vs. scripted usage in `ucli --help`.

---

## **10. Example: Full `/ucli` Command (Python)**
```python
#!/usr/bin/env python3
import sys
from PyInquirer import prompt

def main():
    if not sys.stdout.isatty():
        print("Non-interactive mode. Use --file <file>.")
        return

    questions = [
        {
            "type": "list",
            "name": "action",
            "message": "Select an action:",
            "choices": ["Parse", "Format", "Exit"]
        }
    ]
    answers = prompt(questions)
    print(f"[ucli] Executing: {answers['action']}")

if __name__ == "__main__":
    main()
```

---

This approach ensures your `/ucli` commands are **interactive, user-friendly, and consistent** with vibe-cli’s TUI, while remaining **scriptable and accessible**.