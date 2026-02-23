# Developing uDOS Extensions

Extensions add new functionality to uDOS by hooking into the runtime system. This guide covers the basics of building, testing, and packaging your own extensions.

---

## What is an Extension?

An extension is a modular component that:

- ✅ Hooks into uDOS lifecycle events
- ✅ Adds new commands or features
- ✅ Integrates with existing subsystems
- ✅ Can be enabled/disabled independently

**Examples:** Custom commands, AI integrations, data processors, UI components

---

## Quick Start

### 1. Create Extension Directory

```bash
cd dev
mkdir my-extension
cd my-extension
```

### 2. Create Extension Manifest

Create `extension.json`:

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "My custom uDOS extension",
  "author": "Your Name",
  "license": "MIT",
  "main": "main.py",
  "type": "extension",
  "dependencies": {
    "uDOS": ">=1.3.0"
  },
  "hooks": {
    "on_startup": "hooks.on_startup",
    "on_command": "hooks.on_command"
  },
  "commands": [
    {
      "name": "my-command",
      "handler": "commands.my_command",
      "description": "My custom command"
    }
  ]
}
```

### 3. Create Main Entry Point

Create `main.py`:

```python
"""
My Extension
A custom uDOS extension
"""
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

def initialize():
    """Called when extension is loaded"""
    logger.info("My extension initialized")
    return True

def cleanup():
    """Called when extension is unloaded"""
    logger.info("My extension cleaned up")
    return True
```

### 4. Add Hooks

Create `hooks.py`:

```python
"""Extension hooks"""
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

def on_startup(context):
    """Called on system startup"""
    logger.info("Extension startup hook")
    # Access context.config, context.services, etc.

def on_command(context, command):
    """Called before command execution"""
    logger.info(f"Command intercepted: {command}")
    # Return True to allow, False to block
    return True
```

### 5. Add Commands

Create `commands.py`:

```python
"""Extension commands"""
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

def my_command(args, context):
    """
    My custom command implementation

    Args:
        args: Command arguments
        context: Runtime context
    """
    logger.info(f"My command executed with: {args}")
    print("Hello from my extension!")
    return {"status": "success", "message": "Command executed"}
```

---

## Extension Structure

```
dev/my-extension/
├── extension.json      # Extension manifest (required)
├── main.py            # Entry point (required)
├── hooks.py           # Lifecycle hooks (optional)
├── commands.py        # Command handlers (optional)
├── services.py        # Background services (optional)
├── tests/             # Unit tests (recommended)
│   └── test_main.py
├── requirements.txt   # Python dependencies (if needed)
└── README.md          # Documentation (recommended)
```

---

## Extension API

### Manifest Schema

```json
{
  "name": "string (required)",
  "version": "semver (required)",
  "description": "string (required)",
  "author": "string (optional)",
  "license": "string (optional)",
  "main": "python_module.py (required)",
  "type": "extension | container | plugin",
  "dependencies": {
    "uDOS": "version_constraint"
  },
  "hooks": {
    "on_startup": "module.function",
    "on_shutdown": "module.function",
    "on_command": "module.function",
    "on_event": "module.function"
  },
  "commands": [
    {
      "name": "command-name",
      "handler": "module.function",
      "description": "Command description",
      "args": ["arg1", "arg2"]
    }
  ],
  "services": [
    {
      "name": "service-name",
      "handler": "module.ServiceClass",
      "autostart": true
    }
  ]
}
```

### Available Hooks

| Hook | When Called | Purpose |
|------|-------------|---------|
| `on_startup` | System startup | Initialize resources |
| `on_shutdown` | System shutdown | Cleanup resources |
| `on_command` | Before command execution | Intercept/modify commands |
| `on_event` | System events | React to events |
| `on_config_change` | Config update | Reload configuration |

### Context Object

Available in hooks and commands:

```python
context.config        # System configuration
context.services      # Service registry
context.extensions    # Extension manager
context.logger        # Logger instance
context.data_path     # Data directory path
context.user          # User context
```

---

## Testing Your Extension

### 1. Unit Tests

Create `tests/test_main.py`:

```python
import unittest
from main import initialize, cleanup

class TestMyExtension(unittest.TestCase):

    def test_initialize(self):
        result = initialize()
        self.assertTrue(result)

    def test_cleanup(self):
        result = cleanup()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
python -m pytest tests/
```

### 2. Integration Testing

Install your extension locally:

```bash
# From uDOS root
python -m core.extensions.manager install dev/my-extension
```

Test in uDOS:

```bash
./bin/Launch-uCODE.sh
> my-command
# Your command should execute
```

---

## Common Patterns

### Background Service

```python
# services.py
import threading
import time
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

class MyService:
    def __init__(self, context):
        self.context = context
        self.running = False
        self.thread = None

    def start(self):
        """Start the service"""
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Service started")

    def stop(self):
        """Stop the service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Service stopped")

    def _run(self):
        """Service main loop"""
        while self.running:
            # Do work
            logger.debug("Service tick")
            time.sleep(10)
```

Register in `extension.json`:

```json
{
  "services": [
    {
      "name": "my-service",
      "handler": "services.MyService",
      "autostart": true
    }
  ]
}
```

### Event Listener

```python
# hooks.py
def on_event(context, event):
    """Handle system events"""
    if event.type == "file_changed":
        logger.info(f"File changed: {event.data['path']}")
    elif event.type == "command_completed":
        logger.info(f"Command completed: {event.data['command']}")
```

### Configuration

Access configuration:

```python
def on_startup(context):
    # Read extension config
    config = context.config.get('extensions', {}).get('my-extension', {})
    api_key = config.get('api_key')

    if not api_key:
        logger.warning("API key not configured")
```

User config in `memory/bank/system/config.json`:

```json
{
  "extensions": {
    "my-extension": {
      "api_key": "your-key-here",
      "enabled": true
    }
  }
}
```

---

## Distribution

### 1. Package Structure

```
my-extension/
├── extension.json
├── main.py
├── hooks.py
├── commands.py
├── services.py
├── requirements.txt
├── README.md
├── LICENSE
└── tests/
```

### 2. Create Archive

```bash
cd dev
tar -czf my-extension-1.0.0.tar.gz my-extension/
```

### 3. Distribution Options

- **GitHub Release:** Tag and release on GitHub
- **uDOS Plugin Catalog:** Submit to catalog (if available)
- **Direct Install:** Share archive, users extract to `extensions/`

---

## Best Practices

✅ **Use the logger** — Don't use `print()`, use `get_logger(__name__)`
✅ **Handle errors gracefully** — Catch exceptions, return error status
✅ **Test thoroughly** — Unit tests + integration tests
✅ **Document your API** — Clear README with usage examples
✅ **Version semantically** — Follow semver (major.minor.patch)
✅ **Respect privacy** — Don't access user data without permission
✅ **Be lightweight** — Minimize dependencies and resource usage

❌ **Don't hardcode paths** — Use `context.data_path`
❌ **Don't block the main thread** — Use async or threading for long operations
❌ **Don't assume other extensions** — Check availability before using

---

## Next Steps

✅ **Review examples:** `/dev/examples/extensions/`
✅ **Read API docs:** [API-REFERENCE.md](API-REFERENCE.md)
✅ **Build a container:** [DEVELOP-CONTAINER.md](DEVELOP-CONTAINER.md)

---

**Back to:** [Wiki home](README.md)
