"""Shared types and helpers for LLM extraction providers."""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMExtraction:
    data: dict[str, Any]
    missing_fields: list[str]
    model: str
    confidence: float | None
    provider: str
    strategy: str


def is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, (list, str, dict)) and len(value) == 0)


def missing_fields(model_obj: BaseModel) -> list[str]:
    return [name for name, value in model_obj.model_dump().items() if is_empty(value)]


def completeness(model_obj: BaseModel) -> float:
    """Fraction of top-level fields the model populated (0..1)."""
    fields = model_obj.model_dump()
    if not fields:
        return 0.0
    populated = sum(1 for v in fields.values() if not is_empty(v))
    return round(populated / len(fields), 3)


def with_retries[T](
    fn: Callable[[], T],
    *,
    max_retries: int,
    retryable: tuple[type[Exception], ...],
) -> T:
    """Call fn, retrying transient errors with exponential backoff.

    Backoff is short and deterministic-ish so it stays test-friendly; real
    SDKs (OpenAI, Anthropic) also retry internally, this adds a pipeline-level
    safety net and makes retry behaviour observable/loggable.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except retryable as exc:  # noqa: B902 — provider-specific tuple
            attempt += 1
            if attempt > max_retries:
                logger.warning("LLM call failed after %d retries: %s", max_retries, exc)
                raise
            delay = min(2.0**attempt, 8.0)
            logger.info(
                "LLM transient error (attempt %d/%d), retrying in %.1fs",
                attempt,
                max_retries,
                delay,
            )
            time.sleep(delay)
