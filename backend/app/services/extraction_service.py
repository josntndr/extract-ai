"""LLM structured extraction entrypoint.

Thin facade over the provider-agnostic LLM layer (OpenAI or Anthropic). Given
raw document text and a document type, returns a validated dict matching that
type's Pydantic schema, the fields the model left empty, and provenance
(provider / model / prompt strategy).
"""
from __future__ import annotations

from app.database.models.document import DocumentType
from app.schemas.extraction import EXTRACTION_SCHEMAS
from app.services.llm.base import LLMExtraction
from app.services.llm.factory import run_extraction

# Re-export so existing imports (and tests) keep working.
__all__ = ["LLMExtraction", "extract_structured"]


def extract_structured(
    text: str,
    doc_type: DocumentType,
    *,
    provider: str | None = None,
    strategy_key: str | None = None,
) -> LLMExtraction:
    schema = EXTRACTION_SCHEMAS.get(doc_type)
    if schema is None:
        raise ValueError(f"No extraction schema registered for document type {doc_type}")
    return run_extraction(
        text, doc_type, schema, provider=provider, strategy_key=strategy_key
    )
