"""merge all heads

Revision ID: fcb3e9d30177
Revises: b83fd0664b74, f2c1a5b6d789
Create Date: 2025-08-31 05:20:01.986123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcb3e9d30177'
down_revision: Union[str, None] = ('b83fd0664b74', 'f2c1a5b6d789')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
