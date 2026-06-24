"""Document request/response schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.database.models.document import (
    DocumentSource,
    DocumentStatus,
    DocumentType,
)
from app.schemas.extraction import ExtractionResponse


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    doc_type: DocumentType
    status: DocumentStatus
    source: DocumentSource
    ocr_confidence: float | None
    page_count: int | None
    processing_ms: int | None
    error_message: str | None
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    extracted_text: str | None
    tables: list | None = None
    extraction: ExtractionResponse | None


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class BatchItemResult(BaseModel):
    filename: str
    accepted: bool
    document_id: uuid.UUID | None = None
    error: str | None = None


class BatchUploadResponse(BaseModel):
    """Per-file outcome for a batch upload — partial failures are reported,
    not fatal: valid files are accepted and queued even if siblings fail."""
    total: int
    accepted: int
    rejected: int
    items: list[BatchItemResult]
