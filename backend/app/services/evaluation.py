"""Prompt-strategy evaluation harness.

Runs labelled documents through each prompt strategy (and the configured
provider, or the mock) and scores field-level extraction accuracy. Lets us
answer "which prompt strategy works best, and by how much" with data instead
of vibes — see scripts/eval_prompts.py for the CLI.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.database.models.document import DocumentType
from app.services.extraction_service import extract_structured


def _norm(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, list):
        return {_norm(v) for v in value}
    return value


def field_correct(predicted: Any, expected: Any) -> bool:
    """A field is correct if the (normalised) prediction matches the label.

    Lists are compared as sets (order-insensitive); strings case-insensitively.
    """
    return _norm(predicted) == _norm(expected)


@dataclass
class StrategyScore:
    strategy: str
    provider: str
    samples: int
    fields_evaluated: int
    fields_correct: int

    @property
    def accuracy(self) -> float:
        if not self.fields_evaluated:
            return 0.0
        return round(self.fields_correct / self.fields_evaluated, 3)


def evaluate_strategy(
    fixtures: list[dict[str, Any]],
    doc_type: DocumentType,
    strategy_key: str,
    provider: str | None = None,
) -> StrategyScore:
    """Score one prompt strategy across all fixtures.

    Each fixture is {"text": <doc text>, "expected": {field: value, ...}}.
    Only the fields present in `expected` are scored.
    """
    evaluated = correct = 0
    used_provider = provider or "configured"
    for fixture in fixtures:
        result = extract_structured(
            fixture["text"], doc_type, provider=provider, strategy_key=strategy_key
        )
        used_provider = result.provider
        for field, expected in fixture["expected"].items():
            evaluated += 1
            if field_correct(result.data.get(field), expected):
                correct += 1
    return StrategyScore(
        strategy=strategy_key,
        provider=used_provider,
        samples=len(fixtures),
        fields_evaluated=evaluated,
        fields_correct=correct,
    )


def run_benchmark(
    fixtures: list[dict[str, Any]],
    doc_type: DocumentType,
    strategies: list[str],
    provider: str | None = None,
) -> list[dict[str, Any]]:
    """Benchmark several strategies; returns rows sorted best-accuracy-first."""
    scores = [evaluate_strategy(fixtures, doc_type, s, provider) for s in strategies]
    rows = [{**asdict(s), "accuracy": s.accuracy} for s in scores]
    rows.sort(key=lambda r: r["accuracy"], reverse=True)
    return rows
