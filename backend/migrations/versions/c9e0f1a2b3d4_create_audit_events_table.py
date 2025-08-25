"""create audit events table

Revision ID: c9e0f1a2b3d4
Revises: aa1b2c3d4e5f
Create Date: 2025-06-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c9e0f1a2b3d4"
down_revision: Union[str, None] = "aa1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("org_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("ingestion_jobs.id"), nullable=True),
        sa.Column("batch_id", sa.String(), sa.ForeignKey("import_batches.id"), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
