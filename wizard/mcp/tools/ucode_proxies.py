"""Direct MCP tool proxies for frequently-used uDOS tools.

These are optimized wrappers for high-volume tools:
- health: System health check
- help: Command documentation
- run: Script execution
- read: File content reading
- story: Narrative content
- play: Game execution
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from vibe.core.tools.base import BaseToolConfig, BaseToolState
from vibe.core.tools.ucode.system import UcodeHealth, HealthArgs
from vibe.core.tools.ucode.system import UcodeToken, TokenArgs
from vibe.core.tools.ucode.system import UcodeHelp, HelpArgs
from vibe.core.tools.ucode.workspace import UcodeRun, RunArgs
from vibe.core.tools.ucode.content import UcodeRead, ReadArgs
from vibe.core.tools.ucode.content import UcodeStory, StoryArgs

from .ucode_mcp_registry import MCPToolLane, tool_names


def _get_config() -> BaseToolConfig:
    """Get tool configuration."""
    return BaseToolConfig()


def _get_state() -> BaseToolState:
    """Get tool state."""
    return BaseToolState()


async def proxy_health(check: Optional[str] = None) -> Dict[str, Any]:
    """Health check proxy."""
    try:
        tool = UcodeHealth(config=_get_config(), state=_get_state())
        result = await tool.run(HealthArgs(check=check or ""))
        return {
            "status": "success",
            "tool": "health",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "health",
        }


async def proxy_token(action: str = "generate", ttl: Optional[int] = None) -> Dict[str, Any]:
    """Token generation proxy."""
    try:
        tool = UcodeToken(config=_get_config(), state=_get_state())
        result = await tool.run(TokenArgs(action=action, ttl=ttl))
        return {
            "status": "success",
            "tool": "token",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "token",
        }


async def proxy_help(
    command: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """Help documentation proxy."""
    try:
        tool = UcodeHelp(config=_get_config(), state=_get_state())
        result = await tool.run(HelpArgs(command=command or "", topic=topic or ""))
        return {
            "status": "success",
            "tool": "help",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "help",
        }


async def proxy_run(
    script: str,
    args: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Script execution proxy."""
    try:
        tool = UcodeRun(config=_get_config(), state=_get_state())
        result = await tool.run(
            RunArgs(
                script=script,
                args=args or "",
                env=env or {},
            )
        )
        return {
            "status": "success",
            "tool": "run",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "run",
        }


async def proxy_read(path: str, format: Optional[str] = None) -> Dict[str, Any]:
    """File reading proxy."""
    try:
        tool = UcodeRead(config=_get_config(), state=_get_state())
        result = await tool.run(
            ReadArgs(
                path=path,
                format=format or "auto",
            )
        )
        return {
            "status": "success",
            "tool": "read",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "read",
        }


async def proxy_story(
    story_id: str,
    action: str = "start",
) -> Dict[str, Any]:
    """Story execution proxy."""
    try:
        tool = UcodeStory(config=_get_config(), state=_get_state())
        result = await tool.run(
            StoryArgs(
                story_id=story_id,
                action=action,
            )
        )
        return {
            "status": "success",
            "tool": "story",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "story",
        }


def register_ucode_proxies(mcp_server) -> None:
    """Register high-volume tool proxies with MCP server.

    Args:
        mcp_server: FastMCP server instance.
    """
    @mcp_server.tool()
    def ucode_health(check: Optional[str] = None) -> Dict[str, Any]:
        """Check uDOS system health."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_health(check))
        except RuntimeError:
            return asyncio.run(proxy_health(check))

    @mcp_server.tool()
    def ucode_token(action: str = "generate", ttl: Optional[int] = None) -> Dict[str, Any]:
        """Generate or validate authentication token."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_token(action, ttl))
        except RuntimeError:
            return asyncio.run(proxy_token(action, ttl))

    @mcp_server.tool()
    def ucode_help(command: Optional[str] = None, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get help documentation for uDOS commands."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_help(command, topic))
        except RuntimeError:
            return asyncio.run(proxy_help(command, topic))

    @mcp_server.tool()
    def ucode_run(
        script: str,
        args: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute a uDOS script."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_run(script, args, env))
        except RuntimeError:
            return asyncio.run(proxy_run(script, args, env))

    @mcp_server.tool()
    def ucode_read(path: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Read a file from the vault."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_read(path, format))
        except RuntimeError:
            return asyncio.run(proxy_read(path, format))

    @mcp_server.tool()
    def ucode_story(story_id: str, action: str = "start") -> Dict[str, Any]:
        """Execute a narrative story."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {"status": "error", "message": "Cannot run async tool in running loop"}
            return loop.run_until_complete(proxy_story(story_id, action))
        except RuntimeError:
            return asyncio.run(proxy_story(story_id, action))

    registered_names = {
        "ucode_health",
        "ucode_token",
        "ucode_help",
        "ucode_run",
        "ucode_read",
        "ucode_story",
    }
    expected_names = set(tool_names(MCPToolLane.PROXY))
    if registered_names != expected_names:
        raise RuntimeError(
            f"uCODE proxy MCP registry drift: expected {sorted(expected_names)}, got {sorted(registered_names)}"
        )
