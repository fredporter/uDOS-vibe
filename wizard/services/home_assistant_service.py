"""
Home Assistant Bridge Service
==============================

Minimal contract service for the uDOS ↔ Home Assistant bridge.

Security contract:
- Bridge is disabled by default; must be explicitly enabled in Wizard config.
- LAN-only exposure enforced by Wizard auth layer.
- Admin token required for command execution.
- Only explicitly allowlisted commands may be executed.
"""

from __future__ import annotations

from typing import Any

_BRIDGE_VERSION = "0.1.0"

# Commands explicitly allowed through the bridge.
# Only safe, non-destructive read/control actions appear here.
_COMMAND_ALLOWLIST: set[str] = {
    "uhome.tuner.discover",
    "uhome.tuner.status",
    "uhome.dvr.list_rules",
    "uhome.dvr.schedule",
    "uhome.dvr.cancel",
    "uhome.ad_processing.get_mode",
    "uhome.ad_processing.set_mode",
    "uhome.playback.handoff",
    "uhome.playback.status",
    "system.info",
    "system.capabilities",
}


def get_ha_service() -> HomeAssistantService:
    return HomeAssistantService()


class HomeAssistantService:
    """uDOS Wizard ↔ Home Assistant bridge service."""

    def is_enabled(self) -> bool:
        """Return True if the HA bridge is enabled in Wizard config."""
        try:
            from wizard.services.wizard_config import WizardConfig

            cfg = WizardConfig()
            return bool(cfg.get("ha_bridge_enabled", False))
        except Exception:
            return False

    def status(self) -> dict[str, Any]:
        """Return bridge status and capability summary."""
        enabled = self.is_enabled()
        return {
            "bridge": "udos-ha",
            "version": _BRIDGE_VERSION,
            "status": "ok" if enabled else "disabled",
            "enabled": enabled,
            "command_allowlist_size": len(_COMMAND_ALLOWLIST),
        }

    def discover(self) -> dict[str, Any]:
        """Return available uDOS entities/services discoverable by HA."""
        entities = [
            {
                "id": "udos.system",
                "type": "service",
                "name": "uDOS System",
                "capabilities": ["info", "capabilities"],
            },
            {
                "id": "udos.uhome.tuner",
                "type": "media_source",
                "name": "uHOME Broadcast Tuner",
                "capabilities": ["discover", "status"],
            },
            {
                "id": "udos.uhome.dvr",
                "type": "recorder",
                "name": "uHOME DVR",
                "capabilities": ["list_rules", "schedule", "cancel"],
            },
            {
                "id": "udos.uhome.ad_processing",
                "type": "processor",
                "name": "uHOME Ad Processing",
                "capabilities": ["get_mode", "set_mode"],
            },
            {
                "id": "udos.uhome.playback",
                "type": "media_player",
                "name": "uHOME Playback",
                "capabilities": ["status", "handoff"],
            },
        ]
        return {
            "bridge": "udos-ha",
            "version": _BRIDGE_VERSION,
            "entity_count": len(entities),
            "entities": entities,
        }

    def execute_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute an allowlisted uDOS/uHOME command.

        Raises ValueError for commands not on the allowlist.
        """
        if command not in _COMMAND_ALLOWLIST:
            raise ValueError(f"Command not in allowlist: {command!r}")

        if command == "system.info":
            return self._system_info()
        if command == "system.capabilities":
            return self._system_capabilities()
        if command.startswith("uhome."):
            return self._uhome_dispatch(command, params)

        raise ValueError(f"Unhandled allowlisted command: {command!r}")

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    def _system_info(self) -> dict[str, Any]:
        return {"command": "system.info", "result": {"bridge_version": _BRIDGE_VERSION}}

    def _system_capabilities(self) -> dict[str, Any]:
        return {
            "command": "system.capabilities",
            "result": {"allowlist": sorted(_COMMAND_ALLOWLIST)},
        }

    def _uhome_dispatch(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """Dispatch uHOME commands to the real handler implementations."""
        from wizard.services.uhome_command_handlers import dispatch
        try:
            return dispatch(command, params)
        except KeyError:
            # Graceful fallback for any allowlisted command without a handler yet
            return {
                "command": command,
                "status": "unimplemented",
                "note": f"Handler for {command!r} not yet wired.",
                "params": params,
            }
