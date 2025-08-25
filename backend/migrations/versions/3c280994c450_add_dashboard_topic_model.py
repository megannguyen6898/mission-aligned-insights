"""add dashboard topic model"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c280994c450'
down_revision = '2b3f9d1c92a1'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'dashboard_topics',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('dashboard_topics')
