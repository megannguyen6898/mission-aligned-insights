"""add lineage columns to staging and core tables

Revision ID: 47d816f245d2
Revises: 96a0b401ae34
Create Date: 2025-06-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "47d816f245d2"
down_revision: Union[str, None] = "96a0b401ae34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STAGING_TABLES = [
    "stg_project_info",
    "stg_activities",
    "stg_outcomes",
    "stg_funding_resources",
    "stg_beneficiaries",
]

CORE_TABLES = [
    "projects",
    "activities",
    "outcomes",
    "funding_resources",
    "beneficiaries",
]


LINEAGE_COLUMNS = [
    sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
    sa.Column("external_id", sa.String(), nullable=True),
    sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    sa.Column("row_hash", sa.String(), nullable=True),
    sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id"), nullable=True),
    sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
]


def upgrade() -> None:
    for table in STAGING_TABLES + CORE_TABLES:
        for column in LINEAGE_COLUMNS:
            op.add_column(table, column.copy())


def downgrade() -> None:
    for table in STAGING_TABLES + CORE_TABLES:
        for column in reversed(LINEAGE_COLUMNS):
            op.drop_column(table, column.name)
