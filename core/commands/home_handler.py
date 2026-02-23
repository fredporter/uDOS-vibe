"""HOME command handler - Wizard proxy shim."""

from __future__ import annotations

from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.wizard_proxy_service import dispatch_via_wizard, wizard_proxy_status


class HomeHandler(BaseCommandHandler):
    """Handler for HOME command.

    Core runtime does not call Home Assistant directly.
    HOME commands are proxied to local Wizard APIs.
    """

    def handle(
        self,
        command: str,
        params: list[str],
        grid=None,
        parser=None,
    ) -> dict[str, object]:
        if not params:
            return self._help()

        action = params[0].strip().lower()
        match action:
            case "help" | "?":
                return self._help()
            case "status":
                return self._status()
            case "lights" | "devices" | "call":
                return self._proxy(params)
            case _:
                raise CommandError(
                    code="ERR_COMMAND_NOT_FOUND",
                    message=f"Unknown HOME action '{params[0]}'. Try HOME HELP.",
                    recovery_hint="Use HOME STATUS, HOME LIGHTS, HOME DEVICES, or HOME CALL",
                    level="INFO",
                )

    def _proxy(self, params: list[str]) -> dict[str, object]:
        raw = " ".join(str(part).strip() for part in params if str(part).strip())
        if not raw:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: HOME <STATUS|LIGHTS|DEVICES|CALL> ...",
                recovery_hint="Run HOME HELP for command examples",
                level="INFO",
            )
        return dispatch_via_wizard(f"HOME {raw}")

    def _status(self) -> dict[str, object]:
        status = wizard_proxy_status()
        if status.get("status") == "success":
            status["message"] = "HOME command proxied through local Wizard"
        return status

    def _help(self) -> dict[str, object]:
        return {
            "status": "success",
            "output": (
                "HOME - Wizard-proxied Home Assistant integration\n"
                "  HOME STATUS                        Check local Wizard proxy status\n"
                "  HOME LIGHTS                        List lights via Wizard\n"
                "  HOME LIGHTS ON|OFF <entity_id>     Toggle a light via Wizard\n"
                "  HOME DEVICES                       List entities by domain via Wizard\n"
                "  HOME CALL <domain> <service> [id]  Raw service call via Wizard\n"
            ),
        }
