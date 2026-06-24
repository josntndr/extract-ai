"""CLI: benchmark prompt strategies for resume extraction.

Usage (from backend/):
    python -m scripts.eval_prompts                 # uses configured provider / mock
    LLM_PROVIDER=anthropic python -m scripts.eval_prompts
    python -m scripts.eval_prompts --provider openai

With LLM_MOCK=true (or no API key) this runs against the deterministic stub —
useful in CI to verify the harness end-to-end without spending tokens.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.database.models.document import DocumentType
from app.services.evaluation import run_benchmark

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "resumes.json"
STRATEGIES = ["zero_shot", "few_shot", "cot"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark prompt strategies")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default=None)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    args = parser.parse_args()

    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    rows = run_benchmark(fixtures, DocumentType.RESUME, STRATEGIES, provider=args.provider)

    print(f"\nPrompt-strategy benchmark — {len(fixtures)} resume sample(s)\n")
    print(f"{'strategy':<12}{'provider':<18}{'accuracy':>9}{'correct/total':>16}")
    print("-" * 55)
    for r in rows:
        ratio = f"{r['fields_correct']}/{r['fields_evaluated']}"
        print(f"{r['strategy']:<12}{r['provider']:<18}{r['accuracy']:>8.1%}{ratio:>16}")
    print(f"\nBest: {rows[0]['strategy']} ({rows[0]['accuracy']:.1%})\n")


if __name__ == "__main__":
    main()
