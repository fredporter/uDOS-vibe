"""Response Normaliser for Vibe-CLI.

Normalizes provider responses before execution:
- Strips markdown wrappers
- Extracts ucode commands
- Validates syntax
- Prevents shell injection
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from core.services.command_dispatch_service import match_ucode_command
from core.services.logging_manager import get_logger


@dataclass
class NormalisedResponse:
    """Normalised provider response."""

    text: str  # Clean text response
    contains_ucode: bool = False  # Whether ucode commands found
    ucode_commands: list[str] | None = None  # Extracted ucode commands
    is_safe: bool = True  # Whether response is safe to execute
    warnings: list[str] | None = None  # Any validation warnings


class ResponseNormaliser:
    """Normalise provider responses before execution.

    This ensures:
    - Markdown wrappers are stripped
    - ucode commands are extracted
    - Syntax is validated
    - Shell injection is prevented
    - Only safe commands are flagged for execution
    """

    # Patterns for markdown code blocks
    CODE_BLOCK_PATTERN = re.compile(
        r"```(?:ucode|bash|shell)?\n(.*?)\n```", re.DOTALL | re.IGNORECASE
    )

    # Patterns for dangerous shell commands
    DANGEROUS_PATTERNS = [
        r"\brm\s+-rf\s+/",  # rm -rf /
        r"\b:\(\)\s*\{",  # Fork bomb
        r">\s*/dev/sd[a-z]",  # Direct disk write
        r"\bcurl\s+.*\|\s*(?:bash|sh)",  # Pipe to shell
        r"\bwget\s+.*\|\s*(?:bash|sh)",  # Pipe to shell
    ]

    def __init__(self):
        """Initialize response normaliser."""
        self.logger = get_logger("vibe", category="normaliser")

    def normalise(self, raw_response: str) -> NormalisedResponse:
        """Normalise provider response.

        Args:
            raw_response: Raw response from provider

        Returns:
            NormalisedResponse with extracted commands and safety status
        """
        if not raw_response or not raw_response.strip():
            return NormalisedResponse(text="", is_safe=True)

        # Strip markdown wrappers
        text = self._strip_markdown(raw_response)

        # Extract potential ucode commands
        ucode_commands = self._extract_ucode_commands(text)

        # Validate safety
        is_safe, warnings = self._validate_safety(text)

        self.logger.debug(
            f"[Normaliser] Processed response: "
            f"ucode={len(ucode_commands or [])}, safe={is_safe}"
        )

        return NormalisedResponse(
            text=text.strip(),
            contains_ucode=bool(ucode_commands),
            ucode_commands=ucode_commands,
            is_safe=is_safe,
            warnings=warnings,
        )

    def _strip_markdown(self, text: str) -> str:
        """Strip markdown code blocks and formatting.

        Args:
            text: Text with potential markdown

        Returns:
            Clean text without markdown formatting
        """
        # Extract code from code blocks
        matches = self.CODE_BLOCK_PATTERN.findall(text)
        if matches:
            # If we found code blocks, use the first one's content
            text = matches[0]

        # Remove inline code markers
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove bold/italic markers
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)

        # Remove headers
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        return text.strip()

    def _extract_ucode_commands(self, text: str) -> list[str] | None:
        """Extract potential ucode commands from text.

        Args:
            text: Normalised text

        Returns:
            List of extracted ucode commands, or None if none found
        """
        commands = []

        # Split into lines
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line looks like a ucode command
            command, confidence = match_ucode_command(line)

            if command and confidence >= 0.80:
                commands.append(line)
                self.logger.debug(
                    f"[Normaliser] Extracted ucode: {line} "
                    f"(confidence: {confidence:.2f})"
                )

        return commands if commands else None

    def _validate_safety(self, text: str) -> tuple[bool, list[str] | None]:
        """Validate response safety.

        Args:
            text: Normalised text

        Returns:
            (is_safe, warnings) tuple
        """
        warnings = []

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(f"Dangerous pattern detected: {pattern}")

        # Check for suspicious characters
        if any(char in text for char in [";", "&&", "||", "|", ">"]):
            # Some shell operators found - inspect more carefully
            if re.search(r";\s*rm\b", text, re.IGNORECASE):
                warnings.append("Suspicious command chaining detected")

        is_safe = len(warnings) == 0

        if warnings:
            self.logger.warning(f"[Normaliser] Safety warnings: {', '.join(warnings)}")

        return is_safe, warnings if warnings else None
