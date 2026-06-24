"""Anthropic Claude extraction provider (Structured Outputs via messages.parse).

Uses the Anthropic Python SDK's `client.messages.parse(...)` helper, which
constrains the response to a Pydantic schema and validates it. Per the current
API, Claude Opus 4.x rejects `temperature`, prefilled assistant turns, and
`budget_tokens` — none are sent here.
"""
from __future__ import annotations

from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.database.models.document import DocumentType
from app.services.llm.base import (
    LLMExtraction,
    completeness,
    missing_fields,
    with_retries,
)
from app.services.prompts import PromptStrategy

logger = get_logger(__name__)
PROVIDER = "anthropic"


def extract(
    text: str, doc_type: DocumentType, schema: type[BaseModel], strategy: PromptStrategy
) -> LLMExtraction:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    document_text = text[:120_000]

    def _call() -> BaseModel:
        response = client.messages.parse(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=16_000,
            system=strategy.system(),
            messages=[{"role": "user", "content": strategy.user(document_text, doc_type)}],
            output_format=schema,  # structured output constrained to the schema
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Claude refused the extraction request")
        parsed = response.parsed_output
        if parsed is None:
            raise RuntimeError("Anthropic returned no parsed structured output")
        return parsed

    parsed = with_retries(
        _call,
        max_retries=settings.LLM_MAX_RETRIES,
        retryable=(
            anthropic.RateLimitError,
            anthropic.InternalServerError,
            anthropic.APIConnectionError,
        ),
    )
    return LLMExtraction(
        data=parsed.model_dump(),
        missing_fields=missing_fields(parsed),
        model=settings.ANTHROPIC_MODEL,
        confidence=completeness(parsed),
        provider=PROVIDER,
        strategy=strategy.key,
    )
