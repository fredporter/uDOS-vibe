"""MODE command handler - runtime mode visibility and theme bridge."""

from __future__ import annotations
from typing import Any

from core.commands.base import BaseCommandHandler
from core.commands.skin_handler import SkinHandler
from core.commands.theme_handler import ThemeHandler
from core.services.compact_status_service import format_compact_status
from core.services.dev_state import get_dev_active
from core.services.mode_policy import boundaries_enforced, mode_summary, resolve_runtime_mode
from core.services.progression_contract_service import build_skin_policy_context
from core.services.theme_service import get_theme_service
from core.services.user_service import get_user_manager, is_ghost_mode
from core.services.wizard_mode_state import get_wizard_mode_active
from core.tui.output import OutputToolkit


class ModeHandler(BaseCommandHandler):
    """Handler for MODE command."""

    def __init__(self) -> None:
        super().__init__()
        self.theme = get_theme_service()
        self.theme_handler = ThemeHandler()
        self.skin_handler = SkinHandler()

    def handle(
        self,
        command: str,
        params: list[str],
        grid: Any = None,
        parser: Any = None,
    ) -> dict[str, Any]:
        action = (params[0].lower() if params else "status")
        trailing = params[1:] if len(params) > 1 else []
        match action:
            case "status" | "show" | "list":
                compact = any(str(item).strip().lower() in {"--compact", "compact"} for item in trailing)
                return self._status_payload(compact=compact)
            case "theme":
                return self._theme_payload(params[1:], grid=grid, parser=parser)
            case "help" | "--help" | "-h" | "?":
                return {"status": "success", "output": self._help_text()}
            case _:
                return {
                    "status": "error",
                    "message": "Usage: MODE STATUS | MODE THEME ...",
                    "output": self._help_text(),
                }

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("MODE"),
                "MODE STATUS   Show active runtime mode + boundary flags",
                "MODE STATUS --compact   One-line HUD output with skin/lens/progression",
                "MODE THEME    Theme bridge (LIST|SHOW|SET|CLEAR|<name>)",
                "MODE HELP     Show this help",
            ]
        )

    def _theme_payload(self, params: list[str], grid: Any = None, parser: Any = None) -> dict[str, Any]:
        # Bridge to THEME command so theme controls stay discoverable from MODE.
        result = self.theme_handler.handle("THEME", params, grid=grid, parser=parser)
        output = result.get("output")
        if isinstance(output, str) and output:
            result["output"] = self._tag_retheme_candidate(output, reason="theme-lingo")
        result.setdefault("policy_flag", "theme_lingo")
        return result

    def _tag_retheme_candidate(self, text: str, reason: str) -> str:
        marker = f"[RETHEME-CANDIDATE:{reason}]"
        if marker in text:
            return text
        return f"{text}\n{marker}"

    def _skin_fit_context(self) -> dict[str, Any]:
        user = get_user_manager().current()
        if not user:
            return {"active_skin": self.skin_handler._active_skin(), "fit": "unknown"}

        try:
            from core.services.gameplay_service import get_gameplay_service
        except Exception:
            return {"active_skin": self.skin_handler._active_skin(), "fit": "unknown"}

        progression = get_gameplay_service().progression_snapshot(user.username)
        active_skin = self.skin_handler._active_skin()
        policy = build_skin_policy_context(
            progression=progression,
            selected_skin=active_skin,
            available_skins=self.skin_handler._available_skins(),
        )
        match policy.policy_flag:
            case None:
                fit = "aligned"
            case "skin_lens_unmapped":
                fit = "unmapped"
            case _:
                fit = "mismatch"
        return {
            "active_skin": active_skin,
            "active_lens": policy.active_lens or "unknown",
            "fit": fit,
            "policy_flag": policy.policy_flag,
            "progression": progression,
            "recommended_skins": policy.recommended_skins,
        }

    def _status_payload(self, *, compact: bool = False) -> dict[str, Any]:
        summary = mode_summary()
        active_mode = resolve_runtime_mode().value
        active_theme = self.theme.get_active_message_theme()
        skin_ctx = self._skin_fit_context()
        progression = skin_ctx.get("progression", {})
        stats = progression.get("stats", {}) if isinstance(progression, dict) else {}
        progress = progression.get("progress", {}) if isinstance(progression, dict) else {}
        flags = {
            "ghost_mode": is_ghost_mode(),
            "wizard_mode": get_wizard_mode_active(),
            "dev_mode": bool(get_dev_active()),
            "boundary_enforcement": boundaries_enforced(),
            "retheme_tagging": True,
            "skin_lens_fit": skin_ctx.get("fit", "unknown"),
            "skin_lens_policy_flag": skin_ctx.get("policy_flag"),
        }
        if compact:
            compact_fields: dict[str, Any] = {
                "theme": active_theme,
                "lens": skin_ctx.get("active_lens", "unknown"),
                "skin": skin_ctx.get("active_skin", "default"),
                "fit": skin_ctx.get("fit", "unknown"),
                "xp": stats.get("xp", 0),
                "gold": stats.get("gold", 0),
                "ach": progress.get("achievement_level", 0),
                "enforce": "on" if flags["boundary_enforcement"] else "off",
                "policy": skin_ctx.get("policy_flag"),
            }
            return {
                "status": "success",
                "message": f"Runtime mode: {active_mode}",
                "output": format_compact_status(
                    f"MODE:{active_mode}",
                    compact_fields,
                    order=["theme", "lens", "skin", "fit", "xp", "gold", "ach", "enforce", "policy"],
                ),
                "mode": summary,
                "flags": flags,
            }
        output_lines = [
            OutputToolkit.banner("MODE STATUS"),
            f"Active: {summary['label']} ({active_mode})",
            f"Theme: {active_theme}",
            f"Lens: {skin_ctx.get('active_lens', 'unknown')}",
            f"Skin: {skin_ctx.get('active_skin', 'default')} ({skin_ctx.get('fit', 'unknown')})",
            f"Progression: XP={stats.get('xp', 0)} Gold={stats.get('gold', 0)} AchievementLevel={progress.get('achievement_level', 0)}",
            f"Purpose: {summary['purpose']}",
            f"Policy: {summary['policy']}",
            "",
            "Flags:",
            f"- ghost_mode: {'on' if flags['ghost_mode'] else 'off'}",
            f"- wizard_mode: {'on' if flags['wizard_mode'] else 'off'}",
            f"- dev_mode: {'on' if flags['dev_mode'] else 'off'}",
            f"- boundary_enforcement: {'on' if flags['boundary_enforcement'] else 'off'}",
            f"- retheme_tagging: {'on' if flags['retheme_tagging'] else 'off'}",
            f"- skin_lens_fit: {flags['skin_lens_fit']}",
            (
                f"- skin_lens_policy_flag: {flags['skin_lens_policy_flag']}"
                if flags["skin_lens_policy_flag"]
                else "- skin_lens_policy_flag: none"
            ),
            "",
            "Theme control:",
            "- MODE THEME LIST",
            "- MODE THEME SET <name>",
        ]
        return {
            "status": "success",
            "message": f"Runtime mode: {active_mode}",
            "output": "\n".join(output_lines),
            "mode": summary,
            "flags": flags,
        }
