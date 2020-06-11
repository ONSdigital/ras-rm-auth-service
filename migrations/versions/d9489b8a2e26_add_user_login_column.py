"""add_user_login_column

Revision ID: d9489b8a2e26
Revises: ec404c6ac54c
Create Date: 2020-06-11 14:37:08.510893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9489b8a2e26'
down_revision = 'ec404c6ac54c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'auth.user',
        sa.Column('last_login_date', sa.DateTime, default=None, nullable=True)
    )


def downgrade():
    op.drop_column('user', 'last_login_date')
