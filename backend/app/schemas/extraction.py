"""Structured extraction schemas.

These Pydantic models are passed directly to the OpenAI Structured Outputs API
so the LLM is constrained to return exactly this shape. Adding a new document
type is a matter of defining its model and registering it in EXTRACTION_SCHEMAS.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.database.models.document import DocumentType


# ─── Resume ────────────────────────────────────────────────────────────────
class Education(BaseModel):
    institution: str | None = Field(default=None, description="School or university name")
    degree: str | None = Field(default=None, description="Degree or qualification earned")
    field_of_study: str | None = None
    start_year: str | None = None
    end_year: str | None = None


class Experience(BaseModel):
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = Field(default=None, description="'Present' if current role")
    summary: str | None = Field(default=None, description="One-line summary of responsibilities")


class ResumeData(BaseModel):
    """Structured fields extracted from a resume/CV."""
    name: str | None = Field(default=None, description="Candidate full name")
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = Field(default=None, description="Professional summary or objective")
    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)


# ─── Invoice ───────────────────────────────────────────────────────────────
class InvoiceLineItem(BaseModel):
    description: str | None = Field(default=None, description="What the line item is for")
    quantity: float | None = None
    unit_price: float | None = Field(default=None, description="Price per unit")
    amount: float | None = Field(default=None, description="Line total (quantity × unit price)")


class InvoiceData(BaseModel):
    """Structured fields extracted from an invoice or bill."""
    invoice_number: str | None = Field(default=None, description="Invoice / reference number")
    issue_date: str | None = Field(default=None, description="Date the invoice was issued")
    due_date: str | None = None
    vendor_name: str | None = Field(default=None, description="Company that issued the invoice")
    vendor_address: str | None = None
    bill_to: str | None = Field(default=None, description="Customer the invoice is addressed to")
    currency: str | None = Field(default=None, description="ISO code or symbol, e.g. USD or $")
    subtotal: float | None = None
    tax: float | None = Field(default=None, description="Total tax / VAT amount")
    total: float | None = Field(default=None, description="Grand total amount due")
    line_items: list[InvoiceLineItem] = Field(default_factory=list)


# Registry mapping a document type to its extraction schema.
EXTRACTION_SCHEMAS: dict[DocumentType, type[BaseModel]] = {
    DocumentType.RESUME: ResumeData,
    DocumentType.INVOICE: InvoiceData,
}


# ─── API response ──────────────────────────────────────────────────────────
class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    data: dict
    missing_fields: list[str]
    model: str
    provider: str | None = None
    strategy: str | None = None
    confidence: float | None
    created_at: datetime
