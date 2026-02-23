"""
Example Extension

Demonstrates extension structure and API.
"""

from typing import Dict, Any


def setup():
    """Called when extension is loaded."""
    print("[Example] Extension setup complete")


def handle_command(command: str, params: Dict[str, Any]) -> Any:
    """
    Handle extension commands.

    Args:
        command: Command name (e.g., 'EXAMPLE')
        params: Command parameters

    Returns:
        Command result
    """
    if command == "EXAMPLE":
        message = params.get("message", "Hello from extension!")
        return {
            "status": "success",
            "message": message,
            "extension": "com.udos.example",
        }

    return {"status": "error", "message": f"Unknown command: {command}"}


def hook_system_startup():
    """Called when uDOS starts."""
    print("[Example] System startup hook called")


def hook_command_pre(command: str, params: Dict[str, Any]):
    """
    Called before any command executes.

    Args:
        command: Command being executed
        params: Command parameters
    """
    print(f"[Example] Pre-hook: {command}")


def hook_command_post(command: str, result: Any):
    """
    Called after command executes.

    Args:
        command: Command that was executed
        result: Command result
    """
    print(f"[Example] Post-hook: {command} -> {result}")
