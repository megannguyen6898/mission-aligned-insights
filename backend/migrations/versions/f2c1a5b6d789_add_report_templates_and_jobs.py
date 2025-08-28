"""add report templates and jobs tables

Revision ID: f2c1a5b6d789
Revises: d4f6e7c8b9a1
Create Date: 2025-06-06 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f2c1a5b6d789"
down_revision: Union[str, None] = "d4f6e7c8b9a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "report_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "engine",
            sa.Enum("html", "docx", name="reportengine"),
            nullable=False,
        ),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "report_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column(
            "template_id",
            sa.Integer(),
            sa.ForeignKey("report_templates.id"),
            nullable=False,
        ),
        sa.Column("params_json", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "success", "failed", name="reportjobstatus"),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("output_object_key", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("report_jobs")
    op.drop_table("report_templates")
    op.execute("DROP TYPE IF EXISTS reportjobstatus")
    op.execute("DROP TYPE IF EXISTS reportengine")
