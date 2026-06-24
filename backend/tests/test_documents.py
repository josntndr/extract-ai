"""Document upload, validation, and pipeline tests."""
from __future__ import annotations

import io

from app.database.models.document import (
    Document,
    DocumentSource,
    DocumentStatus,
)


def _make_native_pdf(text: str = "John Doe\njohn@example.com\nSkills: Python FastAPI React") -> bytes:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_upload_rejects_unsupported_type(client, auth_headers):
    files = {"file": ("note.txt", io.BytesIO(b"hello world"), "text/plain")}
    r = client.post("/api/v1/documents", files=files, data={"process_now": "false"}, headers=auth_headers)
    assert r.status_code == 422


def test_upload_rejects_spoofed_content(client, auth_headers):
    # Declares PDF but the bytes are not a PDF.
    files = {"file": ("fake.pdf", io.BytesIO(b"not a real pdf"), "application/pdf")}
    r = client.post("/api/v1/documents", files=files, data={"process_now": "false"}, headers=auth_headers)
    assert r.status_code == 422


def test_upload_requires_auth(client):
    files = {"file": ("r.pdf", io.BytesIO(_make_native_pdf()), "application/pdf")}
    assert client.post("/api/v1/documents", files=files).status_code == 401


def test_upload_and_list(client, auth_headers):
    files = {"file": ("resume.pdf", io.BytesIO(_make_native_pdf()), "application/pdf")}
    r = client.post(
        "/api/v1/documents",
        files=files,
        data={"doc_type": "resume", "process_now": "false"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["filename"] == "resume.pdf"
    assert body["doc_type"] == "resume"
    assert body["status"] == "uploaded"

    listing = client.get("/api/v1/documents", headers=auth_headers).json()
    assert listing["total"] == 1
    assert len(listing["items"]) == 1


def test_pipeline_native_pdf_resume(client, auth_headers, db_session):
    """End-to-end: upload → process (mock LLM) → structured resume data."""
    from app.services.document_pipeline import process_document

    files = {"file": ("resume.pdf", io.BytesIO(_make_native_pdf()), "application/pdf")}
    r = client.post(
        "/api/v1/documents",
        files=files,
        data={"doc_type": "resume", "process_now": "false"},
        headers=auth_headers,
    )
    doc_id = r.json()["id"]

    # Run the pipeline synchronously against the test session.
    document = db_session.get(Document, __import__("uuid").UUID(doc_id))
    process_document(db_session, document)

    detail = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers).json()
    assert detail["status"] == DocumentStatus.COMPLETED.value
    assert detail["source"] == DocumentSource.NATIVE_PDF.value
    assert "John Doe" in (detail["extracted_text"] or "")
    assert detail["extraction"] is not None
    assert detail["extraction"]["data"]["email"] == "john@example.com"
    assert "python" in detail["extraction"]["data"]["skills"]


def test_cannot_access_other_users_document(client, auth_headers, db_session):
    files = {"file": ("resume.pdf", io.BytesIO(_make_native_pdf()), "application/pdf")}
    r = client.post(
        "/api/v1/documents",
        files=files,
        data={"process_now": "false"},
        headers=auth_headers,
    )
    doc_id = r.json()["id"]

    # Second user must not see the first user's document.
    other = {"email": "intruder@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=other)
    token = client.post("/api/v1/auth/login", json=other).json()["access_token"]
    r2 = client.get(f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 404
