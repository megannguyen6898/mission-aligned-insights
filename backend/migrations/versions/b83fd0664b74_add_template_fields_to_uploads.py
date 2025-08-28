"""add template columns to uploads

Revision ID: b83fd0664b74
Revises: 7329a50dd3fa
Create Date: 2024-08-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b83fd0664b74"
down_revision: Union[str, None] = "7329a50dd3fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("uploads") as batch:
        batch.add_column(sa.Column("template_version", sa.String(), nullable=True))
        batch.add_column(sa.Column("errors_json", sa.JSON(), nullable=True))
        batch.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            )
        )
        batch.alter_column(
            "status",
            existing_type=sa.Enum(
                "pending",
                "completed",
                "failed",
                name="uploadfilestatus",
            ),
            type_=sa.Enum(
                "pending",
                "validated",
                "failed",
                "ingested",
                name="uploadfilestatus",
            ),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("uploads") as batch:
        batch.alter_column(
            "status",
            existing_type=sa.Enum(
                "pending",
                "validated",
                "failed",
                "ingested",
                name="uploadfilestatus",
            ),
            type_=sa.Enum(
                "pending",
                "completed",
                "failed",
                name="uploadfilestatus",
            ),
            existing_nullable=False,
        )
        batch.drop_column("updated_at")
        batch.drop_column("errors_json")
        batch.drop_column("template_version")
