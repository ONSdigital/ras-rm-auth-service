"""add account verification date column

Revision ID: a2ab8f75df9c
Revises: 12c104921bb4
Create Date: 2024-04-25 11:59:00.655345

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a2ab8f75df9c"
down_revision = "12c104921bb4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("account_verification_date", sa.DateTime, nullable=True), schema="auth")


def downgrade():
    op.drop_column("user", "account_verification_date", schema="auth")
