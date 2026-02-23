"""WEB command handler - Wizard proxy shim."""

from __future__ import annotations

from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.wizard_proxy_service import dispatch_via_wizard, wizard_proxy_status


class WebHandler(BaseCommandHandler):
    """Handler for WEB command.

    Core runtime does not execute web networking directly.
    WEB commands are proxied to local Wizard APIs.
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
            case "fetch" | "md" | "markdown" | "convert" | "save":
                return self._proxy(params)
            case _ if params[0].startswith("http"):
                return self._proxy(params)
            case _:
                raise CommandError(
                    code="ERR_COMMAND_NOT_FOUND",
                    message=f"Unknown WEB action '{params[0]}'. Try WEB HELP.",
                    recovery_hint="Use WEB FETCH, WEB MD, WEB SAVE, or WEB STATUS",
                    level="INFO",
                )

    def _proxy(self, params: list[str]) -> dict[str, object]:
        raw = " ".join(str(part).strip() for part in params if str(part).strip())
        if not raw:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: WEB <FETCH|MD|SAVE> ...",
                recovery_hint="Run WEB HELP for command examples",
                level="INFO",
            )
        return dispatch_via_wizard(f"WEB {raw}")

    def _status(self) -> dict[str, object]:
        status = wizard_proxy_status()
        if status.get("status") == "success":
            status["message"] = "WEB command proxied through local Wizard"
        return status

    def _help(self) -> dict[str, object]:
        return {
            "status": "success",
            "output": (
                "WEB - Wizard-proxied web operations\n"
                "  WEB FETCH <url>                Fetch raw content via Wizard\n"
                "  WEB MD <url> [--out <file>]    Convert URL to Markdown via Wizard\n"
                "  WEB SAVE <url> <file>          Download URL via Wizard\n"
                "  WEB STATUS                     Check local Wizard proxy status\n"
            ),
        }
