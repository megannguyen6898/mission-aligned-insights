"""add metrics table (post-core)

Revision ID: 00a6b13ed849
Revises: 8517499341a9
Create Date: 2025-08-27 00:32:00.892199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00a6b13ed849'
down_revision: Union[str, None] = 'aa1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("outcome_fk", sa.String(), sa.ForeignKey("outcomes.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("outcome_fk", "name", "recorded_at", name="uq_metric_outcome_name_time"),
    )


def downgrade() -> None:
    op.drop_table("metrics")
