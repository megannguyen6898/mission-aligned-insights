"""create uploads table

Revision ID: 7329a50dd3fa
Revises: 3c280994c450
Create Date: 2024-08-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7329a50dd3fa"
down_revision: Union[str, None] = "3c280994c450"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "failed", name="uploadfilestatus"),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_uploads_id"), "uploads", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_uploads_id"), table_name="uploads")
    op.drop_table("uploads")
    sa.Enum(name="uploadfilestatus").drop(op.get_bind())
