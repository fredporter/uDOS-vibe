# Phase C: MCP Integration Plan

Complete guide for integrating Phase A/B tools into the wizard MCP server.

---

## Overview

**Phase A/B** (Complete): 42 tools as local BaseTool classes
**Phase C** (This): Expose all tools via Model Context Protocol (MCP) server

### Goal
Make all 42 uDOS tools callable from Claude/Mistral through the wizard MCP server, enabling full automation pipeline.

---

## Current State

### Phase A/B Architecture
```
Mistral Vibe CLI
  ↓
  vibe/core/tools/ucode/* (42 BaseTool classes)
  └─ _base.py._dispatch() → CommandDispatcher → uDOS handlers
```

### Phase C Target Architecture
```
Claude/Mistral
  ↓
MCP Client
  ↓
wizard/mcp/mcp_server.py (Wizard MCP Server)
  ↓
  ucode_dispatch tool
  └─ Forward to Phase A/B tools via _dispatch()

  + Individual tool proxies for high-volume tools
  └─ health, verify, run, read, story, etc.
```

---

## Integration Strategy

### Step 1: Create MCP Tool Registry (wizard/mcp/tools/ucode_registry.py)

```python
"""Registry and discovery of uDOS tools for MCP."""

from vibe.core.tools.ucode import system, spatial, data, workspace, content, specialized

def discover_ucode_tools():
    """Auto-discover all ucode tools."""
    modules = [system, spatial, data, workspace, content, specialized]
    tools = {}

    for mod in modules:
        for name in dir(mod):
            obj = getattr(mod, name)
            if hasattr(obj, '__mro__') and any(b.__name__ == 'BaseTool' for b in obj.__mro__):
                tool_name = obj().get_name() if hasattr(obj(), 'get_name') else name.lower()
                tools[tool_name] = obj

    return tools
```

### Step 2: Create MCP Tool Publisher (wizard/mcp/tools/ucode_tools.py)

Publish individual tools as MCP resources:

```python
"""Expose uDOS tools as MCP capabilities."""

async def list_ucode_tools():
    """List all available uDOS tools."""
    tools = discover_ucode_tools()
    return {
        "tools": [
            {
                "name": tool_name,
                "description": tool_cls.description,
                "inputSchema": tool_cls.schema(),
            }
            for tool_name, tool_cls in sorted(tools.items())
        ]
    }

async def call_ucode_tool(tool_name: str, arguments: dict):
    """Call a uDOS tool by name."""
    tools = discover_ucode_tools()
    if tool_name not in tools:
        return {"error": f"Unknown tool: {tool_name}"}

    tool_cls = tools[tool_name]
    # Instantiate and call tool
    config = tool_cls.get_config()
    state = BaseToolState()
    tool = tool_cls(config=config, state=state)
    result = await tool.run(arguments)
    return result
```

### Step 3: Register with MCP Server (wizard/mcp/mcp_server.py)

In the wizard MCP server's resource/tool discovery:

```python
from wizard.mcp.tools.ucode_tools import list_ucode_tools, call_ucode_tool

# In MCP server initialization
server.tools.add_resource("ucode_tools", list_ucode_tools)
server.tools.add_handler("ucode_*", call_ucode_tool)
```

### Step 4: Update Configuration

Update `.vibe/config.toml` to indicate MCP is active:

```toml
[[mcp_servers]]
name = "wizard"
transport = "stdio"
command = "venv/bin/python"
args = ["wizard/mcp/mcp_server.py"]

  [mcp_servers.env]
  PYTHONPATH = "."
  UCODE_AUTO_DISCOVER = "1"  # Enable Phase A/B tool discovery
```

---

## Implementation Checklist

- [ ] **1. Create ucode_registry.py** (30 mins)
  - [ ] Auto-discovery logic
  - [ ] Tool caching
  - [ ] Error handling

- [ ] **2. Create ucode_tools.py** (45 mins)
  - [ ] List implementation
  - [ ] Call handler
  - [ ] Argument parsing
  - [ ] Result formatting

- [ ] **3. Update mcp_server.py** (30 mins)
  - [ ] Import new modules
  - [ ] Register tool publishers
  - [ ] Add MCP route handlers
  - [ ] Test discovery

- [ ] **4. Add High-Volume Tool Proxies** (1 hour)
  - [ ] `ucode_health` → direct MCP tool
  - [ ] `ucode_help` → direct MCP tool
  - [ ] `ucode_run` → direct MCP tool
  - [ ] `ucode_read` → direct MCP tool
  - [ ] `ucode_story` → direct MCP tool

- [ ] **5. Testing** (1 hour)
  - [ ] MCP server startup test
  - [ ] Tool discovery test
  - [ ] Sample tool invocation
  - [ ] Error handling
  - [ ] Full workflow test

- [ ] **6. Documentation** (30 mins)
  - [ ] MCP capabilities doc
  - [ ] Integration examples
  - [ ] Troubleshooting guide

---

## Key Files to Create/Modify

### New Files
- `wizard/mcp/tools/ucode_registry.py` — Tool discovery
- `wizard/mcp/tools/ucode_tools.py` — MCP handlers
- `wizard/mcp/tools/ucode_proxies.py` — High-volume tool wrappers (optional)

### Modified Files
- `wizard/mcp/mcp_server.py` — Register new tools
- `.vibe/config.toml` — Configuration updates
- `wizard/mcp/__init__.py` — Export new modules

---

## MCP Tool Schema

Each tool exposed via MCP needs a JSON schema:

```json
{
  "name": "ucode_health",
  "description": "Run a uDOS health check...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "check": {
        "type": "string",
        "description": "Optional subsystem to check"
      }
    },
    "required": []
  }
}
```

### Auto-Generation from BaseTool

The schema can be auto-generated from Pydantic models:

```python
def tool_to_mcp_schema(tool_cls):
    """Convert BaseTool to MCP schema."""
    args_schema = tool_cls.__args__[0].schema()  # Get Args model
    return {
        "name": tool_cls.get_name(),
        "description": tool_cls.description,
        "inputSchema": {
            "type": "object",
            "properties": args_schema.get("properties", {}),
            "required": args_schema.get("required", []),
        }
    }
```

---

## Execution Flow

### When Claude calls a tool:

```
Claude: "Run the backup script"
  ↓
MCP Client: calls ucode_run with script="backup"
  ↓
wizard/mcp_server.py: handle_tool("ucode_run", {"script": "backup"})
  ↓
ucode_tools.call_ucode_tool("ucode_run", {...})
  ↓
ucode_registry.discover_ucode_tools()["ucode_run"]
  ↓
UcodeRun(config).run(RunArgs(script="backup"))
  ↓
_dispatch("RUN backup")
  ↓
CommandDispatcher → handler
  ↓
{ "status": "ok", "message": "Backup complete", ... }
  ↓
Claude: processes result, generates response
```

---

## High-Volume Tools (Proxies)

For frequently-used tools, create direct MCP wrappers to reduce overhead:

### Proxy Pattern

```python
# wizard/mcp/tools/ucode_proxies.py

@mcp.tool(name="ucode_health")
async def health_proxy(check: str = "") -> dict:
    """Health check proxy."""
    tool = UcodeHealth(config=UcodeConfig(), state=BaseToolState())
    result = await tool.run(HealthArgs(check=check))
    return result

@mcp.tool(name="ucode_help")
async def help_proxy(command: str = "", topic: str = "") -> dict:
    """Help proxy."""
    tool = UcodeHelp(config=UcodeConfig(), state=BaseToolState())
    result = await tool.run(HelpArgs(command=command, topic=topic))
    return result

# ... repeat for run, read, story, play, etc.
```

---

## Error Handling Strategy

### Tool Not Found
```json
{
  "status": "error",
  "message": "Tool 'ucode_unknown' not found",
  "data": {"available_tools": [...]}
}
```

### Invalid Arguments
```json
{
  "status": "error",
  "message": "Invalid arguments for ucode_run",
  "data": {"errors": ["script is required"]}
}
```

### Tool Execution Error
```json
{
  "status": "error",
  "message": "Execution failed: vault not initialized",
  "data": {"suggestion": "Run /ucode-setup first"}
}
```

---

## Performance Considerations

### Caching
- Cache discovered tools (update on MCP server restart)
- Cache tool schemas
- Cache frequently-used tool results

### Optimization
- High-volume tools as direct proxies (no dispatch overhead)
- Async/await for all tool calls
- Stream large results

### Timeout Strategy
```python
TOOL_TIMEOUTS = {
    "ucode_health": 5,      # Quick check
    "ucode_search": 30,     # Can take time
    "ucode_run": 300,       # Scripts can be long
    "ucode_import": 600,    # Large imports
}
```

---

## Testing Phase C

### Unit Tests
- Tool discovery works
- Schemas are valid
- Arguments are parsed correctly

### Integration Tests
- MCP server starts with ucode tools
- Tools are discoverable via MCP
- Tool invocation works end-to-end

### Examples to Test
```bash
# In vibe with wizard MCP running:

> Check my system health
# → ucode_health called

> Run my backup script
# → ucode_run called

> What commands are available?
# → ucode_help called

> Read the installation guide
# → ucode_read called
```

---

## Phase C Benefits

1. **Full Automation**: Claude can now execute any uDOS operation
2. **Extended Reach**: Works with any MCP-compatible client (Claude, LLaMA, etc.)
3. **Consistent Interface**: Same tool definitions across CLI and MCP
4. **Type Safety**: Pydantic validation on all inputs
5. **Advanced Orchestration**: Claude can chain tools intelligently

---

## Timeline Estimate

| Task | Estimate | Cumulative |
|------|----------|-----------|
| Create registry | 30 min | 30 min |
| Create handlers | 45 min | 1h 15m |
| Update MCP server | 30 min | 1h 45m |
| Add proxies | 1 hour | 2h 45m |
| Test suite | 1 hour | 3h 45m |
| Documentation | 30 min | 4h 15m |

**Total: ~4-5 hours** for full Phase C implementation

---

## Success Criteria

- [ ] All 42 tools are discoverable via MCP
- [ ] At least 10 high-volume tools have direct proxies
- [ ] Tool execution succeeds end-to-end
- [ ] Error handling is robust
- [ ] Documentation is complete
- [ ] Tests pass (unit + integration)
- [ ] Performance is acceptable (< 500ms for most tools)

---

## Future Enhancements (Phase D+)

- [ ] Streaming results for long-running operations
- [ ] Progress tracking for batch operations
- [ ] Client-side caching of tool schemas
- [ ] Tool dependency graphs (A depends on B)
- [ ] Automatic workflow generation
- [ ] Tool version management
- [ ] Safe mode (confirm destructive ops)

---

## See Also

- [Phase A/B Status](PHASE-A-STATUS.md)
- [Tools Reference](howto/TOOLS-REFERENCE.md)
- [Architecture Overview](docs/specs/ucode-architecture.md)
- [MCP Server Code](wizard/mcp/mcp_server.py)
