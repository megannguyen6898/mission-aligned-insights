"""create summary tables"""

from alembic import op
import sqlalchemy as sa


revision = "aa1b2c3d4e5f"
down_revision = "47d816f245d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_summary",
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("total_received", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_spent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_beneficiaries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_per_beneficiary", sa.Float(), nullable=True),
    )

    op.create_table(
        "monthly_rollups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("total_received", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_spent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_beneficiaries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_per_beneficiary", sa.Float(), nullable=True),
        sa.Column("source_system", sa.String(), nullable=False, server_default="derived"),
        sa.UniqueConstraint("project_fk", "month", name="uq_rollup_project_month"),
    )

    op.create_table(
        "metrics_summary",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("metric_name", sa.String(), nullable=False),
        sa.Column("total_value", sa.Float(), nullable=True),
        sa.UniqueConstraint("project_fk", "metric_name", name="uq_metric_project_name"),
    )


def downgrade() -> None:
    op.drop_table("metrics_summary")
    op.drop_table("monthly_rollups")
    op.drop_table("project_summary")
