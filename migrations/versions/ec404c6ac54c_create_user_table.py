"""create user table

Revision ID: ec404c6ac54c
Revises:
Create Date: 2018-09-06 15:09:52.587025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec404c6ac54c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(150), unique=True),
        sa.Column('hash', sa.Text, nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False)
    )


def downgrade():
    op.drop_table('user')
