"""Text extraction: classify native-PDF vs scanned vs image, then extract.

Native PDFs → PyMuPDF text layer with layout-aware reading order, plus
pdfplumber table extraction. Scanned PDFs / images → rasterise and OCR.
Output can be rendered as flat text or Markdown (tables → GFM tables).
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any

from app.core.logging import get_logger
from app.database.models.document import DocumentSource
from app.services.ocr_service import run_ocr

logger = get_logger(__name__)

# A PDF page with fewer extractable characters than this is treated as scanned.
_NATIVE_TEXT_MIN_CHARS = 40

IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
PDF_CONTENT_TYPES = {"application/pdf"}


@dataclass
class Table:
    page: int
    rows: list[list[str]]  # row-major; cells normalised to strings ("" for empty)


@dataclass
class ExtractionOutput:
    text: str
    source: DocumentSource
    page_count: int
    ocr_confidence: float | None = None
    per_page_confidence: list[float] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)

    def tables_as_dicts(self) -> list[dict[str, Any]]:
        return [{"page": t.page, "rows": t.rows} for t in self.tables]


def _ordered_page_text(page) -> str:
    """Extract a page's text in human reading order.

    PyMuPDF returns text blocks with bounding boxes; sorting by (top, left)
    reconstructs reading order across multi-column / mixed layouts better than
    raw stream order.
    """
    blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
    text_blocks = [b for b in blocks if len(b) >= 5 and b[4].strip()]
    text_blocks.sort(key=lambda b: (round(b[1] / 10), b[0]))  # band by y, then x
    return "\n".join(b[4].strip() for b in text_blocks)


def _extract_tables(data: bytes) -> list[Table]:
    """Extract tables from a native PDF with pdfplumber."""
    tables: list[Table] = []
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page_no, page in enumerate(pdf.pages, start=1):
                for raw in page.extract_tables() or []:
                    rows = [[(cell or "").strip() for cell in row] for row in raw if row]
                    if rows:
                        tables.append(Table(page=page_no, rows=rows))
    except Exception as exc:  # noqa: BLE001 — table extraction is best-effort
        logger.warning("Table extraction failed: %s", exc)
    return tables


def _extract_pdf(data: bytes) -> ExtractionOutput:
    import fitz  # PyMuPDF

    doc = fitz.open(stream=data, filetype="pdf")
    page_count = doc.page_count
    native_chunks: list[str] = []
    native_chars = 0

    for page in doc:
        ordered = _ordered_page_text(page)
        native_chunks.append(ordered)
        native_chars += len(ordered.strip())

    avg_chars = native_chars / page_count if page_count else 0
    if avg_chars >= _NATIVE_TEXT_MIN_CHARS:
        logger.info("Detected native PDF (avg %.0f chars/page)", avg_chars)
        doc.close()
        return ExtractionOutput(
            text="\n\n".join(native_chunks).strip(),
            source=DocumentSource.NATIVE_PDF,
            page_count=page_count,
            tables=_extract_tables(data),
        )

    # Scanned PDF: rasterise each page and OCR it.
    logger.info("Detected scanned PDF (avg %.0f chars/page) — running OCR", avg_chars)
    ocr_texts: list[str] = []
    confidences: list[float] = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        result = run_ocr(pix.tobytes("png"))
        ocr_texts.append(result.text)
        confidences.append(result.confidence)
    doc.close()

    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return ExtractionOutput(
        text="\n\n".join(ocr_texts).strip(),
        source=DocumentSource.SCANNED_OCR,
        page_count=page_count,
        ocr_confidence=mean_conf,
        per_page_confidence=confidences,
    )


def _extract_image(data: bytes) -> ExtractionOutput:
    result = run_ocr(data)
    return ExtractionOutput(
        text=result.text.strip(),
        source=DocumentSource.IMAGE_OCR,
        page_count=1,
        ocr_confidence=result.confidence,
        per_page_confidence=[result.confidence],
    )


def extract_text(data: bytes, content_type: str) -> ExtractionOutput:
    """Dispatch to the right extractor based on MIME type."""
    if content_type in PDF_CONTENT_TYPES:
        return _extract_pdf(data)
    if content_type in IMAGE_CONTENT_TYPES:
        return _extract_image(data)
    raise ValueError(f"Unsupported content type for extraction: {content_type}")


def table_to_markdown(rows: list[list[str]]) -> str:
    """Render a table (row-major) as a GitHub-flavoured Markdown table."""
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    padded = [r + [""] * (width - len(r)) for r in rows]
    header, *body = padded
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * width) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(lines)


def to_markdown(output: ExtractionOutput) -> str:
    """Render extracted content as Markdown: body text followed by any tables."""
    parts = [output.text]
    for i, table in enumerate(output.tables, start=1):
        parts.append(f"\n\n### Table {i} (page {table.page})\n\n{table_to_markdown(table.rows)}")
    return "".join(parts).strip()
