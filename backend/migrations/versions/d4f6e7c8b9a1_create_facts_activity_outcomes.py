"""create facts table for activities and outcomes"""

from alembic import op
import sqlalchemy as sa

revision = "d4f6e7c8b9a1"
down_revision = "c9e0f1a2b3d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "facts_activity_outcomes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_fk", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=True),
        sa.Column("activities", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("beneficiaries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("spend", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("facts_activity_outcomes")
