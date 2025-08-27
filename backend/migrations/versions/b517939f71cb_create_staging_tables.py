"""create staging tables"""

from alembic import op
import sqlalchemy as sa

revision = 'b517939f71cb'
down_revision = 'e1b312d4e3b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    common = [
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("upload_id", sa.String(), nullable=False),
        sa.Column("row_num", sa.Integer(), nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.Column("parse_errors", sa.JSON(), nullable=True),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String(), nullable=True),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
    ]
    for table in [
        "stg_project_info",
        "stg_activities",
        "stg_outcomes",
        "stg_funding_resources",
        "stg_beneficiaries",
    ]:
        op.create_table(table, *common)  # type: ignore[arg-type]


def downgrade() -> None:
    for table in [
        "stg_project_info",
        "stg_activities",
        "stg_outcomes",
        "stg_funding_resources",
        "stg_beneficiaries",
    ]:
        op.drop_table(table)
