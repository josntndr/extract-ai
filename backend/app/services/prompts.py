"""Prompt-engineering strategies for structured document extraction.

A "strategy" turns (document_text, doc_type) into the system prompt + user
message a provider should send. Keeping these declarative lets us benchmark
strategies against each other (see scripts/eval_prompts.py) and swap them via
the LLM_PROMPT_STRATEGY setting without touching provider code.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.database.models.document import DocumentType

_BASE_SYSTEM = (
    "You are a meticulous document data-extraction engine. Extract the requested "
    "fields from the document text exactly as written. Do not invent or infer "
    "values that are not present — leave a field null (or an empty list) when the "
    "information is genuinely absent. Normalise obvious formatting (dates, phone "
    "numbers) but never fabricate data."
)

# A compact, generic worked example used by the few-shot strategy. It is
# deliberately doc-type-agnostic so it nudges format discipline without biasing
# field values for any one document type.
_FEW_SHOT = (
    "\n\nExample of correct behaviour:\n"
    "TEXT: 'Acme Corp. Contact: jane@acme.io. Phone not listed.'\n"
    "→ name/company: 'Acme Corp', email: 'jane@acme.io', phone: null "
    "(absent fields stay null; present fields are copied verbatim)."
)

_COT = (
    "\n\nBefore producing the structured result, reason silently in this order: "
    "(1) locate each requested field in the text, (2) decide whether the value is "
    "actually present or merely implied, (3) normalise formatting. Only populate a "
    "field when step (2) finds explicit evidence. Return only the structured data."
)


@dataclass
class PromptStrategy:
    key: str
    system_suffix: str = ""

    def system(self) -> str:
        return _BASE_SYSTEM + self.system_suffix

    def user(self, text: str, doc_type: DocumentType) -> str:
        return (
            f"Document type: {doc_type.value}\n\n"
            f"--- DOCUMENT TEXT START ---\n{text}\n--- DOCUMENT TEXT END ---"
        )


STRATEGIES: dict[str, PromptStrategy] = {
    "zero_shot": PromptStrategy(key="zero_shot"),
    "few_shot": PromptStrategy(key="few_shot", system_suffix=_FEW_SHOT),
    "cot": PromptStrategy(key="cot", system_suffix=_COT),
}


def get_strategy(key: str) -> PromptStrategy:
    return STRATEGIES.get(key, STRATEGIES["zero_shot"])
