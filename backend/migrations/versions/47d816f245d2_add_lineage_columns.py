"""no-op: lineage columns already created earlier

Revision ID: 47d816f245d2
Revises: b517939f71cb
Create Date: 2025-06-05 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "47d816f245d2"
down_revision: Union[str, None] = "b517939f71cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # no-op: core + staging already have lineage columns
    pass

def downgrade() -> None:
    # no-op
    pass
