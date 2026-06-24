"""Tests for the provider-agnostic LLM layer, prompt strategies, and eval harness."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.database.models.document import DocumentType
from app.services.evaluation import field_correct, run_benchmark
from app.services.extraction_service import extract_structured
from app.services.prompts import STRATEGIES, get_strategy

FIXTURES = Path(__file__).parent / "fixtures" / "resumes.json"
RESUME = "John Doe\njohn@example.com\nSkills: Python, FastAPI, Docker"


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_extraction_runs_for_both_providers_in_mock(provider):
    # With LLM_MOCK active (conftest sets OPENAI_MOCK), both providers route to
    # the deterministic stub — no network, no keys required.
    result = extract_structured(RESUME, DocumentType.RESUME, provider=provider)
    assert result.data["name"] == "John Doe"
    assert result.data["email"] == "john@example.com"
    assert "python" in result.data["skills"]
    assert result.provider.startswith("mock")
    assert result.strategy in STRATEGIES


@pytest.mark.parametrize("strategy", ["zero_shot", "few_shot", "cot"])
def test_prompt_strategies_are_wired(strategy):
    result = extract_structured(RESUME, DocumentType.RESUME, strategy_key=strategy)
    assert result.strategy == strategy
    s = get_strategy(strategy)
    assert s.system()  # non-empty system prompt
    assert "DOCUMENT TEXT START" in s.user(RESUME, DocumentType.RESUME)


def test_field_correct_normalisation():
    assert field_correct("John Doe", "john doe")
    assert field_correct(["Python", "SQL"], ["sql", "python"])  # order-insensitive
    assert not field_correct("Jane", "John")


def test_benchmark_produces_ranked_metrics():
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = run_benchmark(fixtures, DocumentType.RESUME, ["zero_shot", "few_shot", "cot"])
    assert len(rows) == 3
    # sorted best-first, each row carries a 0..1 accuracy and field counts
    assert rows[0]["accuracy"] >= rows[-1]["accuracy"]
    for r in rows:
        assert 0.0 <= r["accuracy"] <= 1.0
        assert r["fields_evaluated"] > 0
