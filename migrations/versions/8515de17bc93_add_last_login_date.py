"""create user table

Revision ID: 8515de17bc93
Revises:
Create Date: 2020-10-06 14:12:37.423902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8515de17bc93'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('last_login_date', sa.String(100), default=None, nullable=True)
    )


def downgrade():
    pass
