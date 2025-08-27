"""add project activity outcome metric tables

Revision ID: 2b3f9d1c92a1
Revises: 05afe5410c0b
Create Date: 2025-06-05 05:22:43.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b3f9d1c92a1'
down_revision: Union[str, None] = '05afe5410c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(): 
    pass

def downgrade():
    pass
