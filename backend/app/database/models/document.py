"""Document model: an uploaded file and its processing state."""
from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, JSONType, TimestampMixin, UUIDMixin, enum_values

if TYPE_CHECKING:
    from app.database.models.extraction import Extraction
    from app.database.models.user import User


class DocumentType(str, enum.Enum):
    INVOICE = "invoice"
    CONTRACT = "contract"
    RESUME = "resume"
    MEDICAL_FORM = "medical_form"
    BUSINESS_REPORT = "business_report"
    UNKNOWN = "unknown"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentSource(str, enum.Enum):
    """How text was obtained from the file."""
    NATIVE_PDF = "native_pdf"
    SCANNED_OCR = "scanned_ocr"
    IMAGE_OCR = "image_ocr"
    UNKNOWN = "unknown"


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    doc_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type", values_callable=enum_values),
        default=DocumentType.UNKNOWN,
        nullable=False,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", values_callable=enum_values),
        default=DocumentStatus.UPLOADED,
        nullable=False,
        index=True,
    )
    source: Mapped[DocumentSource] = mapped_column(
        Enum(DocumentSource, name="document_source", values_callable=enum_values),
        default=DocumentSource.UNKNOWN,
        nullable=False,
    )

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Tables extracted from the document, as a list of {page, rows: [[cell,...]]}.
    tables: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    page_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    processing_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped[User] = relationship(back_populates="documents")
    extraction: Mapped[Extraction | None] = relationship(
        back_populates="document", cascade="all, delete-orphan", uselist=False
    )
