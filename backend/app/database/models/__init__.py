"""Import all models so Alembic + SQLAlchemy can discover them."""
from app.database.models.document import Document, DocumentStatus, DocumentType
from app.database.models.extraction import Extraction
from app.database.models.refresh_token import RefreshToken
from app.database.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "RefreshToken",
    "Document",
    "DocumentStatus",
    "DocumentType",
    "Extraction",
]
