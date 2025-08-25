"""create import_batches table

Revision ID: 96a0b401ae34
Revises: 0d3e31806d61
Create Date: 2025-06-05 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "96a0b401ae34"
down_revision: Union[str, None] = "0d3e31806d61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_system", sa.String(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("triggered_by_user_id", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "success", "failed", name="batchstatus"),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("error_json", sa.JSON()),
    )
    op.add_column(
        "ingestion_jobs",
        sa.Column("import_batch_id", sa.String(), nullable=False),
    )
    op.create_foreign_key(
        "fk_ingestion_jobs_import_batch_id",
        "ingestion_jobs",
        "import_batches",
        ["import_batch_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ingestion_jobs_import_batch_id",
        "ingestion_jobs",
        type_="foreignkey",
    )
    op.drop_column("ingestion_jobs", "import_batch_id")
    op.drop_table("import_batches")
    sa.Enum(name="batchstatus").drop(op.get_bind())
