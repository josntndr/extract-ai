"""Declarative base and shared column mixins."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# JSONB on Postgres (indexable, binary); JSON elsewhere (e.g. SQLite in tests).
JSONType = JSONB().with_variant(JSON(), "sqlite")


def enum_values(enum_cls: type) -> list[str]:
    """values_callable for SQLAlchemy Enum columns.

    Stores the enum member's *value* (e.g. "user") rather than its NAME
    ("USER"). This matches the lowercase labels our Alembic migrations create
    for the Postgres enum types — without it, SQLAlchemy sends "USER" and
    Postgres rejects it as an invalid enum value.
    """
    return [member.value for member in enum_cls]


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
