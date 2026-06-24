"""File storage abstraction. Local filesystem now; S3-ready interface."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from app.core.config import settings


class LocalStorage:
    """Stores files under STORAGE_DIR/uploads/<owner>/<uuid><ext>."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base = Path(base_dir or settings.STORAGE_DIR)
        self.uploads = self.base / "uploads"
        self.uploads.mkdir(parents=True, exist_ok=True)

    def save(self, owner_id: uuid.UUID, original_name: str, data: bytes) -> str:
        ext = Path(original_name).suffix.lower()
        owner_dir = self.uploads / str(owner_id)
        owner_dir.mkdir(parents=True, exist_ok=True)
        key = f"{owner_id}/{uuid.uuid4().hex}{ext}"
        (self.base / "uploads" / key).write_bytes(data)
        return key

    def path(self, storage_key: str) -> Path:
        return self.uploads / storage_key

    def read(self, storage_key: str) -> bytes:
        return self.path(storage_key).read_bytes()

    def delete(self, storage_key: str) -> None:
        target = self.path(storage_key)
        if target.exists():
            target.unlink()

    def purge_owner(self, owner_id: uuid.UUID) -> None:
        shutil.rmtree(self.uploads / str(owner_id), ignore_errors=True)


def get_storage() -> LocalStorage:
    # When STORAGE_BACKEND == "s3" this is where an S3Storage would be returned.
    return LocalStorage()
