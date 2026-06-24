"""Upload validation: extension, MIME, magic-bytes, and size checks."""
from __future__ import annotations

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
}

# Magic-byte signatures to defend against spoofed content types / extensions.
_MAGIC_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
)


class FileValidationError(ValueError):
    """Raised when an uploaded file fails a validation rule."""


def _extension(filename: str) -> str:
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot != -1 else ""


def sniff_content_type(data: bytes) -> str | None:
    for signature, content_type in _MAGIC_SIGNATURES:
        if data.startswith(signature):
            return content_type
    return None


def validate_upload(filename: str, declared_content_type: str, data: bytes) -> str:
    """Validate an upload and return the trusted (sniffed) content type.

    Raises FileValidationError on any failure.
    """
    if not data:
        raise FileValidationError("Empty file")

    if len(data) > settings.max_upload_bytes:
        raise FileValidationError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    ext = _extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported extension '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    if declared_content_type not in ALLOWED_CONTENT_TYPES:
        raise FileValidationError(f"Unsupported content type '{declared_content_type}'")

    sniffed = sniff_content_type(data)
    if sniffed is None:
        raise FileValidationError("File content does not match a supported type")

    # jpg/jpeg both map to image/jpeg at the magic-byte level.
    return sniffed
