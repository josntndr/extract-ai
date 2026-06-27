"""Selects the configured LLM provider and handles mock mode."""
from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.database.models.document import DocumentType
from app.services.llm.base import LLMExtraction, completeness, missing_fields
from app.services.prompts import PromptStrategy, get_strategy

logger = get_logger(__name__)


def _provider_key() -> str:
    return settings.LLM_PROVIDER


def _api_key_for(provider: str) -> str:
    return settings.OPENAI_API_KEY if provider == "openai" else settings.ANTHROPIC_API_KEY


def _should_mock(provider: str) -> bool:
    # Explicit mock flag, legacy OPENAI_MOCK, or simply no key configured.
    return settings.LLM_MOCK or settings.OPENAI_MOCK or not _api_key_for(provider)


def _mock_extraction(schema: type[BaseModel], text: str, strategy: PromptStrategy) -> LLMExtraction:
    """Deterministic stub used for local dev / CI without spending tokens."""
    payload: dict[str, Any] = {}
    lowered = text.lower()
    fields = schema.model_fields
    if "name" in fields:
        payload["name"] = next((ln.strip() for ln in text.splitlines() if ln.strip()), None)
    if "email" in fields and "@" in text:
        token = next((t for t in text.split() if "@" in t), None)
        payload["email"] = token.strip(".,;") if token else None
    if "skills" in fields:
        payload["skills"] = [
            kw for kw in ("python", "fastapi", "react", "sql", "docker") if kw in lowered
        ]
    # Invoice-shaped heuristics so the mock yields a usable demo result too.
    if "invoice_number" in fields:
        m = re.search(r"invoice\s*#?\s*[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        payload["invoice_number"] = m.group(1) if m else None
    if "total" in fields:
        m = re.search(r"total[^0-9]{0,20}([0-9][0-9,]*\.?[0-9]*)", text, re.IGNORECASE)
        payload["total"] = float(m.group(1).replace(",", "")) if m else None
    if "vendor_name" in fields:
        payload["vendor_name"] = next(
            (ln.strip() for ln in text.splitlines() if ln.strip()), None
        )
    parsed = schema.model_validate(payload)
    return LLMExtraction(
        data=parsed.model_dump(),
        missing_fields=missing_fields(parsed),
        model="mock",
        confidence=completeness(parsed),
        provider=f"mock:{_provider_key()}",
        strategy=strategy.key,
    )


def run_extraction(
    text: str,
    doc_type: DocumentType,
    schema: type[BaseModel],
    *,
    provider: str | None = None,
    strategy_key: str | None = None,
) -> LLMExtraction:
    """Dispatch a structured extraction to the chosen provider (or the mock)."""
    provider = provider or _provider_key()
    strategy = get_strategy(strategy_key or settings.LLM_PROMPT_STRATEGY)

    if _should_mock(provider):
        logger.info("LLM mock active (provider=%s) — returning stub extraction", provider)
        return _mock_extraction(schema, text, strategy)

    if provider == "anthropic":
        from app.services.llm import anthropic_provider

        return anthropic_provider.extract(text, doc_type, schema, strategy)

    from app.services.llm import openai_provider

    return openai_provider.extract(text, doc_type, schema, strategy)
