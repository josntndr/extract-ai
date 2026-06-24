"""OpenAI GPT-4o extraction provider (Structured Outputs)."""
from __future__ import annotations

from pydantic import BaseModel

from app.core.config import settings
from app.database.models.document import DocumentType
from app.services.llm.base import (
    LLMExtraction,
    completeness,
    missing_fields,
    with_retries,
)
from app.services.prompts import PromptStrategy

PROVIDER = "openai"


def extract(
    text: str, doc_type: DocumentType, schema: type[BaseModel], strategy: PromptStrategy
) -> LLMExtraction:
    from openai import APIConnectionError, InternalServerError, OpenAI, RateLimitError

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    document_text = text[:120_000]  # keep token usage bounded

    def _call() -> BaseModel:
        completion = client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": strategy.system()},
                {"role": "user", "content": strategy.user(document_text, doc_type)},
            ],
            response_format=schema,  # constrains output to the Pydantic schema
            temperature=0,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no parsed structured output")
        return parsed

    parsed = with_retries(
        _call,
        max_retries=settings.LLM_MAX_RETRIES,
        retryable=(RateLimitError, InternalServerError, APIConnectionError),
    )
    return LLMExtraction(
        data=parsed.model_dump(),
        missing_fields=missing_fields(parsed),
        model=settings.OPENAI_MODEL,
        confidence=completeness(parsed),
        provider=PROVIDER,
        strategy=strategy.key,
    )
