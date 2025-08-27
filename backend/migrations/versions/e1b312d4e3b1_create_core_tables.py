"""create core domain tables"""

from alembic import op
import sqlalchemy as sa


revision = "e1b312d4e3b1"
down_revision = "96a0b401ae34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_org_id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("name", sa.String()),
        sa.Column("org_name", sa.String()),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("country", sa.String()),
        sa.Column("region", sa.String()),
        sa.Column("sdg_goal", sa.String()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String()),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String()),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("owner_org_id", "project_id", name="uq_project_org_pid"),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("date", sa.Date()),
        sa.Column("activity_type", sa.String()),
        sa.Column("activity_name", sa.String()),
        sa.Column("beneficiaries_reached", sa.Integer()),
        sa.Column("location", sa.String()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String()),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String()),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("project_fk", "activity_name", "date", name="uq_activity_natural"),
    )

    op.create_table(
        "outcomes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("date", sa.Date()),
        sa.Column("outcome_metric", sa.String()),
        sa.Column("value", sa.Float()),
        sa.Column("unit", sa.String()),
        sa.Column("method", sa.String()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String()),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String()),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("project_fk", "outcome_metric", "date", name="uq_outcome_natural"),
    )

    op.create_table(
        "funding_resources",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("date", sa.Date()),
        sa.Column("funding_source", sa.String()),
        sa.Column("received", sa.Float()),
        sa.Column("spent", sa.Float()),
        sa.Column("volunteer_hours", sa.Float()),
        sa.Column("staff_hours", sa.Float()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String()),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String()),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint(
            "project_fk", "funding_source", "date", name="uq_funding_natural"
        ),
    )

    op.create_table(
        "beneficiaries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("date", sa.Date()),
        sa.Column("group", sa.String()),
        sa.Column("count", sa.Integer()),
        sa.Column("demographic_info", sa.String()),
        sa.Column("location", sa.String()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_system", sa.String(), nullable=False, server_default="excel"),
        sa.Column("external_id", sa.String()),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("row_hash", sa.String()),
        sa.Column("import_batch_id", sa.String(), sa.ForeignKey("import_batches.id")),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("project_fk", "group", "date", name="uq_beneficiary_natural"),
    )


def downgrade() -> None:
    op.drop_table("beneficiaries")
    op.drop_table("funding_resources")
    op.drop_table("outcomes")
    op.drop_table("activities")
    op.drop_table("projects")

