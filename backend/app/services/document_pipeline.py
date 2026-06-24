"""End-to-end document processing pipeline.

Orchestrates: load file → extract text (native/OCR) → LLM structured
extraction → persist results. Runs synchronously here; the same function is
designed to be dispatched to a background worker (see app/workers) unchanged.
"""
from __future__ import annotations

import time

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.models.document import Document, DocumentStatus, DocumentType
from app.database.models.extraction import Extraction
from app.services.extraction_service import extract_structured
from app.services.storage import get_storage
from app.services.text_extractor import extract_text

logger = get_logger(__name__)


def process_document(db: Session, document: Document) -> Document:
    """Process a single uploaded document in place, committing state transitions."""
    started = time.perf_counter()
    document.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        data = get_storage().read(document.storage_key)

        # 1. Text extraction (native PDF text layer or OCR).
        extraction_out = extract_text(data, document.content_type)
        document.extracted_text = extraction_out.text
        document.source = extraction_out.source
        document.page_count = extraction_out.page_count
        document.ocr_confidence = extraction_out.ocr_confidence
        document.tables = extraction_out.tables_as_dicts() or None

        if not extraction_out.text.strip():
            raise ValueError("No text could be extracted from the document")

        # 2. LLM structured extraction (only for types we have a schema for).
        if document.doc_type != DocumentType.UNKNOWN:
            llm = extract_structured(extraction_out.text, document.doc_type)
            extraction = document.extraction or Extraction(document_id=document.id)
            extraction.data = llm.data
            extraction.missing_fields = llm.missing_fields
            extraction.model = llm.model
            extraction.provider = llm.provider
            extraction.strategy = llm.strategy
            extraction.confidence = llm.confidence
            document.extraction = extraction

        document.status = DocumentStatus.COMPLETED
        document.error_message = None
    except Exception as exc:  # noqa: BLE001 — record failure, don't crash the request
        logger.exception("Document processing failed for %s", document.id)
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)[:1000]
    finally:
        document.processing_ms = int((time.perf_counter() - started) * 1000)
        db.commit()
        db.refresh(document)

    return document
