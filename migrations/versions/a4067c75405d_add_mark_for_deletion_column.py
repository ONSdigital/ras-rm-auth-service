"""migrations/manual_scripts/add_mark_for_deletion_column.sql

Revision ID: a4067c75405d
Revises: d9489b8a2e26
Create Date: 2020-09-17 15:12:42.795113

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a4067c75405d"
down_revision = "d9489b8a2e26"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("mark_for_deletion", sa.Boolean(), server_default=sa.schema.DefaultClause("0"), nullable=False),
        schema="auth",
    )


def downgrade():
    op.drop_column("user", "mark_for_deletion", schema="auth")
