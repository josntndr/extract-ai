"""Structured extraction result produced by the LLM for a document."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.database.models.document import Document


class Extraction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "extractions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    # The validated, structured payload (shape depends on doc_type).
    data: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)
    # Field names the model could not confidently populate.
    missing_fields: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    document: Mapped[Document] = relationship(back_populates="extraction")
