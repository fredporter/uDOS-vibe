"""Canonical cloud provider schema + failover policy for uCODE cloud mode."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto
import json
from typing import Callable


class CloudProvider(StrEnum):
    MISTRAL = auto()
    OPENROUTER = auto()
    OPENAI = auto()
    ANTHROPIC = auto()
    GEMINI = auto()


class ProviderApiStyle(StrEnum):
    OPENAI_CHAT = auto()
    ANTHROPIC_MESSAGES = auto()
    GEMINI_GENERATE_CONTENT = auto()


class FailoverReason(StrEnum):
    NONE = auto()
    AUTH_MISSING = auto()
    AUTH_ERROR = auto()
    RATE_LIMIT = auto()
    UNREACHABLE = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class CloudProviderContract:
    provider: CloudProvider
    api_style: ProviderApiStyle
    api_base: str
    api_key_env_vars: tuple[str, ...]
    default_model: str
    model_env_var: str
    timeout_seconds: int


@dataclass(frozen=True)
class PreparedCloudRequest:
    url: str
    headers: dict[str, str]
    payload: dict[str, object]
    timeout_seconds: int
    model_name: str


@dataclass(frozen=True)
class CloudAttemptResult:
    provider: CloudProvider
    ok: bool
    response_text: str
    model: str
    reason: FailoverReason
    detail: str


def canonical_cloud_provider_contracts() -> dict[CloudProvider, CloudProviderContract]:
    return {
        CloudProvider.MISTRAL: CloudProviderContract(
            provider=CloudProvider.MISTRAL,
            api_style=ProviderApiStyle.OPENAI_CHAT,
            api_base="https://api.mistral.ai/v1",
            api_key_env_vars=("MISTRAL_API_KEY", "STAGING_MISTRAL_API_KEY"),
            default_model="mistral-small-latest",
            model_env_var="MISTRAL_MODEL",
            timeout_seconds=15,
        ),
        CloudProvider.OPENROUTER: CloudProviderContract(
            provider=CloudProvider.OPENROUTER,
            api_style=ProviderApiStyle.OPENAI_CHAT,
            api_base="https://openrouter.ai/api/v1",
            api_key_env_vars=("OPENROUTER_API_KEY",),
            default_model="openai/gpt-4o-mini",
            model_env_var="OPENROUTER_MODEL",
            timeout_seconds=20,
        ),
        CloudProvider.OPENAI: CloudProviderContract(
            provider=CloudProvider.OPENAI,
            api_style=ProviderApiStyle.OPENAI_CHAT,
            api_base="https://api.openai.com/v1",
            api_key_env_vars=("OPENAI_API_KEY",),
            default_model="gpt-4o-mini",
            model_env_var="OPENAI_MODEL",
            timeout_seconds=20,
        ),
        CloudProvider.ANTHROPIC: CloudProviderContract(
            provider=CloudProvider.ANTHROPIC,
            api_style=ProviderApiStyle.ANTHROPIC_MESSAGES,
            api_base="https://api.anthropic.com/v1",
            api_key_env_vars=("ANTHROPIC_API_KEY",),
            default_model="claude-3-5-sonnet-latest",
            model_env_var="ANTHROPIC_MODEL",
            timeout_seconds=20,
        ),
        CloudProvider.GEMINI: CloudProviderContract(
            provider=CloudProvider.GEMINI,
            api_style=ProviderApiStyle.GEMINI_GENERATE_CONTENT,
            api_base="https://generativelanguage.googleapis.com/v1beta",
            api_key_env_vars=("GEMINI_API_KEY", "GOOGLE_API_KEY"),
            default_model="gemini-1.5-flash",
            model_env_var="GEMINI_MODEL",
            timeout_seconds=20,
        ),
    }


def normalize_cloud_provider(raw: str) -> CloudProvider | None:
    token = (raw or "").strip().lower().replace("-", "_")
    aliases = {
        "mistral": CloudProvider.MISTRAL,
        "openrouter": CloudProvider.OPENROUTER,
        "openai": CloudProvider.OPENAI,
        "anthropic": CloudProvider.ANTHROPIC,
        "gemini": CloudProvider.GEMINI,
        "google_gemini": CloudProvider.GEMINI,
        "google": CloudProvider.GEMINI,
    }
    return aliases.get(token)


def resolve_cloud_provider_chain(env_getter: Callable[[str], str]) -> list[CloudProvider]:
    chain_raw = env_getter("VIBE_CLOUD_PROVIDER_CHAIN")
    parsed_chain = [
        normalize_cloud_provider(token)
        for token in chain_raw.split(",")
        if token.strip()
    ]
    explicit = [provider for provider in parsed_chain if provider is not None]
    if explicit:
        return _dedupe_chain(explicit)

    primary = normalize_cloud_provider(env_getter("VIBE_PRIMARY_CLOUD_PROVIDER"))
    secondary = normalize_cloud_provider(env_getter("VIBE_SECONDARY_CLOUD_PROVIDER"))
    defaults = [
        CloudProvider.MISTRAL,
        CloudProvider.OPENROUTER,
        CloudProvider.OPENAI,
        CloudProvider.ANTHROPIC,
        CloudProvider.GEMINI,
    ]
    candidate = [provider for provider in (primary, secondary) if provider is not None]
    return _dedupe_chain([*candidate, *defaults])


def _dedupe_chain(chain: list[CloudProvider]) -> list[CloudProvider]:
    result: list[CloudProvider] = []
    for provider in chain:
        if provider not in result:
            result.append(provider)
    return result


def resolve_provider_api_key(
    contract: CloudProviderContract,
    env_getter: Callable[[str], str],
) -> str:
    for key_name in contract.api_key_env_vars:
        value = (env_getter(key_name) or "").strip()
        if value:
            return value
    return ""


def prepare_cloud_request(
    contract: CloudProviderContract,
    prompt: str,
    env_getter: Callable[[str], str],
) -> PreparedCloudRequest:
    model_name = (env_getter(contract.model_env_var) or contract.default_model).strip() or contract.default_model
    match contract.api_style:
        case ProviderApiStyle.OPENAI_CHAT:
            return PreparedCloudRequest(
                url=f"{contract.api_base}/chat/completions",
                headers={},
                payload={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout_seconds=contract.timeout_seconds,
                model_name=model_name,
            )
        case ProviderApiStyle.ANTHROPIC_MESSAGES:
            return PreparedCloudRequest(
                url=f"{contract.api_base}/messages",
                headers={"anthropic-version": "2023-06-01"},
                payload={
                    "model": model_name,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout_seconds=contract.timeout_seconds,
                model_name=model_name,
            )
        case ProviderApiStyle.GEMINI_GENERATE_CONTENT:
            return PreparedCloudRequest(
                url=f"{contract.api_base}/models/{model_name}:generateContent",
                headers={},
                payload={"contents": [{"parts": [{"text": prompt}]}]},
                timeout_seconds=contract.timeout_seconds,
                model_name=model_name,
            )
        case _:
            raise ValueError(f"Unsupported provider API style: {contract.api_style}")


def attach_auth(
    contract: CloudProviderContract,
    req: PreparedCloudRequest,
    api_key: str,
) -> PreparedCloudRequest:
    headers = dict(req.headers)
    url = req.url
    match contract.provider:
        case CloudProvider.ANTHROPIC:
            headers["x-api-key"] = api_key
        case CloudProvider.GEMINI:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}key={api_key}"
        case _:
            headers["Authorization"] = f"Bearer {api_key}"
    return PreparedCloudRequest(
        url=url,
        headers=headers,
        payload=req.payload,
        timeout_seconds=req.timeout_seconds,
        model_name=req.model_name,
    )


def parse_cloud_response(
    contract: CloudProviderContract,
    response_json: dict[str, object],
) -> str:
    match contract.api_style:
        case ProviderApiStyle.OPENAI_CHAT:
            choices = response_json.get("choices")
            if not isinstance(choices, list) or not choices:
                return ""
            first = choices[0]
            if not isinstance(first, dict):
                return ""
            message = first.get("message")
            if not isinstance(message, dict):
                return ""
            return _extract_message_content(message.get("content"))
        case ProviderApiStyle.ANTHROPIC_MESSAGES:
            content = response_json.get("content")
            if not isinstance(content, list):
                return ""
            parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "text":
                    continue
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            return "\n".join(parts).strip()
        case ProviderApiStyle.GEMINI_GENERATE_CONTENT:
            candidates = response_json.get("candidates")
            if not isinstance(candidates, list) or not candidates:
                return ""
            first = candidates[0]
            if not isinstance(first, dict):
                return ""
            content = first.get("content")
            if not isinstance(content, dict):
                return ""
            parts = content.get("parts")
            if not isinstance(parts, list):
                return ""
            out: list[str] = []
            for part in parts:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    out.append(text.strip())
            return "\n".join(out).strip()
        case _:
            return ""


def _extract_message_content(raw_content: object) -> str:
    if isinstance(raw_content, str):
        return raw_content.strip()
    if isinstance(raw_content, list):
        parts: list[str] = []
        for item in raw_content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        return "\n".join(parts).strip()
    return ""


def classify_failover_reason(status_code: int, detail: str = "") -> FailoverReason:
    if status_code in {401, 403}:
        return FailoverReason.AUTH_ERROR
    if status_code == 429:
        return FailoverReason.RATE_LIMIT
    if status_code == 0 or status_code in {408, 502, 503, 504}:
        return FailoverReason.UNREACHABLE
    if status_code >= 500:
        return FailoverReason.UNREACHABLE
    return FailoverReason.UNKNOWN


def should_failover(reason: FailoverReason) -> bool:
    return reason in {
        FailoverReason.AUTH_MISSING,
        FailoverReason.AUTH_ERROR,
        FailoverReason.RATE_LIMIT,
        FailoverReason.UNREACHABLE,
    }


def summarize_attempts(attempts: list[CloudAttemptResult]) -> str:
    compact = [
        f"{attempt.provider.value}:{attempt.reason.value}"
        for attempt in attempts
    ]
    return json.dumps(compact)
