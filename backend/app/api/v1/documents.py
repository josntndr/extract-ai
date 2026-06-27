"""Document endpoints: upload + process, list, retrieve, delete."""
from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.logging import get_logger
from app.database.models.document import Document, DocumentStatus, DocumentType
from app.database.models.user import User
from app.database.session import SessionLocal, get_db
from app.schemas.document import (
    BatchItemResult,
    BatchUploadResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentResponse,
)
from app.services.document_pipeline import process_document
from app.services.storage import get_storage
from app.utils.files import FileValidationError, validate_upload

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


def _run_pipeline(document_id: uuid.UUID) -> None:
    """Background task body: open its own session and process the document.

    Defensive by design — a background task must never raise into the worker;
    failures are logged and (where possible) recorded on the document.
    """
    db = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is not None:
            process_document(db, document)
    except Exception:  # noqa: BLE001 — never let a background task crash the worker
        logger.exception("Background processing failed for %s", document_id)
    finally:
        db.close()


async def _read_capped(file: UploadFile) -> bytes:
    """Read an upload in chunks, aborting once it exceeds the configured cap.

    Prevents memory exhaustion: we never buffer more than max_upload_bytes,
    so an oversized (or unbounded) body is rejected instead of being read
    fully into RAM first.
    """
    limit = settings.max_upload_bytes
    total = 0
    parts: list[bytes] = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise FileValidationError(
                f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        parts.append(chunk)
    return b"".join(parts)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(DocumentType.RESUME),
    process_now: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    try:
        data = await _read_capped(file)
        trusted_type = validate_upload(file.filename or "upload", file.content_type or "", data)
    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    storage_key = get_storage().save(current_user.id, file.filename or "upload", data)
    document = Document(
        owner_id=current_user.id,
        filename=file.filename or "upload",
        content_type=trusted_type,
        size_bytes=len(data),
        storage_key=storage_key,
        doc_type=doc_type,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    if process_now:
        # Offload heavy OCR/LLM work so the upload request returns quickly.
        background_tasks.add_task(_run_pipeline, document.id)

    return document


@router.post("/batch", response_model=BatchUploadResponse, status_code=status.HTTP_207_MULTI_STATUS)
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    doc_type: DocumentType = Form(DocumentType.RESUME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BatchUploadResponse:
    """Validate and queue many documents at once.

    Each file is handled independently: a bad file is rejected with its reason
    while valid siblings are still accepted and queued (partial-failure
    semantics). Returns 207 Multi-Status with a per-file breakdown.
    """
    results: list[BatchItemResult] = []
    for file in files:
        name = file.filename or "upload"
        try:
            data = await _read_capped(file)
            trusted_type = validate_upload(name, file.content_type or "", data)
        except FileValidationError as exc:
            results.append(BatchItemResult(filename=name, accepted=False, error=str(exc)))
            continue

        storage_key = get_storage().save(current_user.id, name, data)
        document = Document(
            owner_id=current_user.id,
            filename=name,
            content_type=trusted_type,
            size_bytes=len(data),
            storage_key=storage_key,
            doc_type=doc_type,
            status=DocumentStatus.UPLOADED,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        background_tasks.add_task(_run_pipeline, document.id)
        results.append(BatchItemResult(filename=name, accepted=True, document_id=document.id))

    accepted = sum(1 for r in results if r.accepted)
    return BatchUploadResponse(
        total=len(results),
        accepted=accepted,
        rejected=len(results) - accepted,
        items=results,
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: DocumentStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> DocumentListResponse:
    base = select(Document).where(Document.owner_id == current_user.id)
    if status_filter:
        base = base.where(Document.status == status_filter)

    total = db.scalar(
        select(func.count()).select_from(base.order_by(None).subquery())
    )
    items = list(
        db.scalars(
            base.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        ).all()
    )
    return DocumentListResponse(items=items, total=total or 0)


def _get_owned_document(document_id: uuid.UUID, db: Session, user: User) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    return _get_owned_document(document_id, db, current_user)


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    document = _get_owned_document(document_id, db, current_user)
    background_tasks.add_task(_run_pipeline, document.id)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    document = _get_owned_document(document_id, db, current_user)
    get_storage().delete(document.storage_key)
    db.delete(document)
    db.commit()
