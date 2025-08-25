"""create ingestion jobs table

Revision ID: 0d3e31806d61
Revises: 7329a50dd3fa
Create Date: 2024-08-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0d3e31806d61"
down_revision: Union[str, None] = "7329a50dd3fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("upload_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "success", "failed", name="ingestionjobstatus"),
            server_default="queued",
            nullable=False,
        ),
        sa.Column("error_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_jobs_id"), "ingestion_jobs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingestion_jobs_id"), table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")
    sa.Enum(name="ingestionjobstatus").drop(op.get_bind())
