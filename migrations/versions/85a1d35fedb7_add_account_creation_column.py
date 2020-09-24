"""migrations/manual_scripts/add_account_creation_column.sql

Revision ID: 85a1d35fedb7
Revises: a4067c75405d
Create Date: 2020-09-23 14:29:06.345140

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '85a1d35fedb7'
down_revision = 'a4067c75405d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('account_creation_date', sa.DateTime,
                  server_default=str(datetime(2020, 6, 15, 15, 34, 52)),
                  nullable=False),
        schema="auth"
    )


def downgrade():
    op.drop_column('user', 'account_creation_date', schema="auth")
