from __future__ import annotations

from core.services.cloud_provider_policy import (
    CloudProvider,
    FailoverReason,
    canonical_cloud_provider_contracts,
    classify_failover_reason,
    parse_cloud_response,
    prepare_cloud_request,
    resolve_cloud_provider_chain,
)


def test_resolve_cloud_provider_chain_prefers_explicit_chain() -> None:
    env = {
        "VIBE_CLOUD_PROVIDER_CHAIN": "openrouter,openai,anthropic",
    }
    chain = resolve_cloud_provider_chain(lambda key: env.get(key, ""))
    assert chain == [
        CloudProvider.OPENROUTER,
        CloudProvider.OPENAI,
        CloudProvider.ANTHROPIC,
    ]


def test_prepare_and_parse_openai_style_response() -> None:
    contracts = canonical_cloud_provider_contracts()
    contract = contracts[CloudProvider.OPENAI]
    req = prepare_cloud_request(contract, "hello", lambda _key: "")
    assert req.url.endswith("/chat/completions")
    assert req.model_name == contract.default_model

    parsed = parse_cloud_response(
        contract,
        {
            "choices": [
                {
                    "message": {
                        "content": "hello from openai",
                    }
                }
            ]
        },
    )
    assert parsed == "hello from openai"


def test_prepare_and_parse_gemini_response() -> None:
    contracts = canonical_cloud_provider_contracts()
    contract = contracts[CloudProvider.GEMINI]
    req = prepare_cloud_request(contract, "hello", lambda _key: "")
    assert req.url.endswith(":generateContent")
    assert req.model_name == contract.default_model

    parsed = parse_cloud_response(
        contract,
        {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "hello from gemini"}]
                    }
                }
            ]
        },
    )
    assert parsed == "hello from gemini"


def test_classify_failover_reason() -> None:
    assert classify_failover_reason(401) == FailoverReason.AUTH_ERROR
    assert classify_failover_reason(429) == FailoverReason.RATE_LIMIT
    assert classify_failover_reason(503) == FailoverReason.UNREACHABLE
    assert classify_failover_reason(418) == FailoverReason.UNKNOWN
