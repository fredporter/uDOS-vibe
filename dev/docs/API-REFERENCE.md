# uDOS API Reference

This document provides a reference for the uDOS APIs available to extensions and containers.

---

## Core Services

### Logging

```python
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Configuration

```python
# Access via context in hooks
def on_startup(context):
    config = context.config
    
    # System config
    log_level = config.get('logging', {}).get('level', 'INFO')
    
    # Extension config
    ext_config = config.get('extensions', {}).get('my-extension', {})
    api_key = ext_config.get('api_key')
```

### Service Registry

```python
def on_startup(context):
    # Access registered services
    services = context.services
    
    # Get specific service
    if 'database' in services:
        db = services['database']
        db.connect()
```

### Event System

```python
def on_event(context, event):
    """
    Handle system events
    
    Event types:
    - file_changed: File system change
    - command_completed: Command finished
    - config_changed: Configuration updated
    - service_started: Service initialized
    - service_stopped: Service shut down
    """
    event_type = event.type
    event_data = event.data
    
    if event_type == "file_changed":
        path = event_data['path']
        logger.info(f"File changed: {path}")
```

---

## Extension API

### Manifest Structure

See [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md#extension-api) for full schema.

### Required Functions

```python
def initialize():
    """
    Called when extension is loaded
    
    Returns:
        bool: True if initialization successful
    """
    return True

def cleanup():
    """
    Called when extension is unloaded
    
    Returns:
        bool: True if cleanup successful
    """
    return True
```

### Hook Functions

```python
def on_startup(context):
    """System startup hook"""
    pass

def on_shutdown(context):
    """System shutdown hook"""
    pass

def on_command(context, command):
    """
    Command interception hook
    
    Returns:
        bool: True to allow command, False to block
    """
    return True

def on_config_change(context, config):
    """Configuration change hook"""
    pass
```

### Command Handlers

```python
def my_command(args, context):
    """
    Command handler
    
    Args:
        args: Command arguments (list)
        context: Runtime context
        
    Returns:
        dict: Result with status and message
    """
    return {
        "status": "success",
        "message": "Command completed",
        "data": {}
    }
```

---

## Container API

### Lifecycle Scripts

All scripts should:
- ✅ Exit with code 0 on success
- ✅ Exit with non-zero on failure
- ✅ Use `set -e` for error handling
- ✅ Log to stdout/stderr

### Environment Variables

Available in container:

```bash
UDOS_ROOT          # uDOS installation root
UDOS_VERSION       # uDOS version
CONTAINER_NAME     # This container's name
CONTAINER_VERSION  # This container's version
DATA_PATH          # Container data directory
LOG_PATH           # Container log directory
CONFIG_PATH        # Container config directory
```

### Health Check Exit Codes

```bash
0   # Healthy
1   # Unhealthy
2   # Starting (not ready yet)
```

---

## Data Paths

### Extension Data

```python
# Access via context
def on_startup(context):
    data_path = context.data_path
    # e.g., /path/to/uDOS/memory/extensions/my-extension/
    
    # Create data files
    config_file = os.path.join(data_path, 'config.json')
    with open(config_file, 'w') as f:
        json.dump({...}, f)
```

### Container Data

```bash
# In container scripts
DATA_PATH=/app/data
mkdir -p "$DATA_PATH"
echo "data" > "$DATA_PATH/file.txt"
```

---

## Common Patterns

### Async Tasks

```python
import asyncio
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

async def async_operation():
    """Async operation"""
    await asyncio.sleep(1)
    return "result"

def my_command(args, context):
    """Command using async"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_operation())
    return {"status": "success", "data": result}
```

### Background Tasks

```python
import threading
import time

class BackgroundWorker:
    def __init__(self, context):
        self.context = context
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._work)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _work(self):
        while self.running:
            # Do work
            time.sleep(10)
```

### Error Handling

```python
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

def my_command(args, context):
    try:
        # Do work
        result = process(args)
        return {
            "status": "success",
            "data": result
        }
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return {
            "status": "error",
            "message": f"Invalid input: {e}"
        }
    except Exception as e:
        logger.exception("Unexpected error")
        return {
            "status": "error",
            "message": "An unexpected error occurred"
        }
```

### Configuration Management

```python
import json
import os

def load_config(context):
    """Load extension config"""
    config_path = os.path.join(context.data_path, 'config.json')
    
    # Use defaults if not found
    if not os.path.exists(config_path):
        return {
            "api_key": None,
            "timeout": 30,
            "enabled": True
        }
    
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(context, config):
    """Save extension config"""
    config_path = os.path.join(context.data_path, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
```

---

## Type Hints

```python
from typing import Dict, Any, Optional, List

def my_command(
    args: List[str],
    context: 'RuntimeContext'
) -> Dict[str, Any]:
    """
    Command with type hints
    
    Args:
        args: Command arguments
        context: Runtime context
        
    Returns:
        Result dictionary with status
    """
    return {"status": "success"}

def on_startup(context: 'RuntimeContext') -> None:
    """Startup hook with type hints"""
    pass
```

---

## Testing Utilities

### Mock Context

```python
# tests/test_my_extension.py
import unittest
from unittest.mock import Mock

class TestMyExtension(unittest.TestCase):
    
    def setUp(self):
        # Create mock context
        self.context = Mock()
        self.context.config = {}
        self.context.services = {}
        self.context.data_path = '/tmp/test'
        self.context.logger = Mock()
    
    def test_command(self):
        from commands import my_command
        result = my_command(['arg1'], self.context)
        self.assertEqual(result['status'], 'success')
```

---

## Versioning

### Extension Versions

Follow semantic versioning (semver):

```
MAJOR.MINOR.PATCH
1.0.0 — Initial release
1.1.0 — Add new feature (backward compatible)
1.1.1 — Fix bug (backward compatible)
2.0.0 — Breaking change
```

### API Compatibility

Check uDOS version:

```python
def on_startup(context):
    udos_version = context.version
    major, minor, patch = map(int, udos_version.split('.'))
    
    if major < 1 or (major == 1 and minor < 3):
        logger.error("uDOS 1.3+ required")
        return False
    
    return True
```

---

## Environment Variables

### System Variables

Available to extensions:

```python
import os

UDOS_ROOT = os.getenv('UDOS_ROOT')
UDOS_VERSION = os.getenv('UDOS_VERSION')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### Custom Variables

Set in extension config or container definition.

---

## Security

### Input Validation

```python
def my_command(args, context):
    # Validate input
    if not args:
        return {"status": "error", "message": "Arguments required"}
    
    # Sanitize paths
    path = args[0]
    if '..' in path or path.startswith('/'):
        return {"status": "error", "message": "Invalid path"}
    
    # Proceed safely
    safe_path = os.path.join(context.data_path, path)
    # ...
```

### Secret Management

```python
def on_startup(context):
    # Read secrets from environment (not config files)
    api_key = os.getenv('MY_EXTENSION_API_KEY')
    
    if not api_key:
        logger.error("API key not configured")
        return False
    
    # Store securely (in memory only, don't log)
    context.services['my_extension'] = {
        'api_key': api_key  # Only in memory
    }
```

---

## Further Reading

- **Extension Development:** [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md)
- **Container Development:** [DEVELOP-CONTAINER.md](DEVELOP-CONTAINER.md)
- **uDOS Documentation:** `/docs/` (root level)
- **Source Code:** Browse uDOS source for examples

---

**Back to:** [Wiki home](README.md)
