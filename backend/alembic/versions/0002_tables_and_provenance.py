"""add documents.tables and extraction provider/strategy provenance

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-25
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("tables", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("extractions", sa.Column("provider", sa.String(length=64), nullable=True))
    op.add_column("extractions", sa.Column("strategy", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("extractions", "strategy")
    op.drop_column("extractions", "provider")
    op.drop_column("documents", "tables")
