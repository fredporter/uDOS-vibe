"""
Vibe Ask Service

Provides natural language query handling via language models (local or cloud).
Integrates with OK/Vibe system for intelligent responses.
"""

from typing import Dict, Any, Optional
from enum import StrEnum, auto
import os
import shutil
import subprocess

from core.services.logging_manager import get_logger


class AskBackend(StrEnum):
    """Supported ask backends."""

    OLLAMA = auto()
    NONE = auto()


class VibeAskService:
    """Handle natural language queries and provide intelligent responses."""

    def __init__(self):
        """Initialize ask service."""
        self.logger = get_logger("vibe-ask-service")
        self.model: Optional[str] = None
        self.backend: AskBackend = AskBackend.NONE
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize language model (local or remote)."""
        self.logger.debug("Initializing ask backend")
        model = os.getenv("VIBE_ASK_MODEL", "mistral")
        if shutil.which("ollama"):
            self.backend = AskBackend.OLLAMA
            self.model = model
            self.logger.info(f"Ask backend ready: {self.backend.value} ({self.model})")
            return

        self.backend = AskBackend.NONE
        self.model = None
        self.logger.warning("Ask backend unavailable: ollama not found in PATH")

    def _run_backend(self, prompt: str) -> str:
        """Execute prompt against configured backend and return response text."""
        match self.backend:
            case AskBackend.OLLAMA:
                if not self.model:
                    raise RuntimeError("Ask backend misconfigured: missing model")
                result = subprocess.run(
                    ["ollama", "run", self.model, prompt],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    message = result.stderr.strip() or "ollama backend error"
                    raise RuntimeError(message)
                return result.stdout.strip()
            case AskBackend.NONE:
                raise RuntimeError("No ask backend available (install/start Ollama)")
            case _:
                raise RuntimeError(f"Unsupported ask backend: {self.backend.value}")

    def query(self, prompt: str) -> Dict[str, Any]:
        """
        Send a natural language query to the language model.

        Args:
            prompt: User query

        Returns:
            Dict with response and metadata
        """
        if not prompt or not prompt.strip():
            return {
                "status": "error",
                "message": "Empty query",
            }

        self.logger.info(f"Processing query: {prompt[:50]}...")
        if self.backend == AskBackend.NONE:
            return {
                "status": "error",
                "message": "Ask backend unavailable. Install/start Ollama and retry.",
                "backend": self.backend.value,
            }

        try:
            response = self._run_backend(prompt)
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Ask backend timeout",
                "backend": self.backend.value,
            }
        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
                "backend": self.backend.value,
            }

        return {
            "status": "success",
            "query": prompt,
            "response": response,
            "model": self.model,
            "backend": self.backend.value,
            "confidence": 0.85,
        }

    def explain(self, topic: str, detail_level: str = "medium") -> Dict[str, Any]:
        """
        Get an explanation of a topic.

        Args:
            topic: Topic to explain
            detail_level: Level of detail (brief|medium|detailed)

        Returns:
            Dict with explanation
        """
        self.logger.info(f"Explaining: {topic} (detail: {detail_level})")
        prompt = (
            f"Explain '{topic}' at {detail_level} detail level."
            " Keep structure clear and practical."
        )
        result = self.query(prompt)
        if result.get("status") != "success":
            return result
        return {
            "status": "success",
            "topic": topic,
            "detail_level": detail_level,
            "explanation": result.get("response", ""),
            "model": self.model,
            "backend": self.backend.value,
        }

    def suggest(self, context: str) -> Dict[str, Any]:
        """
        Get suggestions based on context.

        Args:
            context: Context for suggestions

        Returns:
            Dict with suggestions
        """
        self.logger.info(f"Getting suggestions for: {context[:30]}...")
        prompt = (
            "Provide three concise actionable suggestions for this context:\n"
            f"{context}\n"
            "Format as three separate lines."
        )
        result = self.query(prompt)
        if result.get("status") != "success":
            return result

        raw = result.get("response", "")
        suggestions = [line.strip("-* ").strip() for line in raw.splitlines() if line.strip()]
        if not suggestions:
            suggestions = [raw] if raw else []

        return {
            "status": "success",
            "context": context,
            "suggestions": suggestions[:3],
            "model": self.model,
            "backend": self.backend.value,
        }


# Global singleton
_ask_service: Optional[VibeAskService] = None


def get_ask_service() -> VibeAskService:
    """Get or create the global ask service."""
    global _ask_service
    if _ask_service is None:
        _ask_service = VibeAskService()
    return _ask_service
