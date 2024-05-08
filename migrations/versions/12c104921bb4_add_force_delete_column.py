"""add force delete column

Revision ID: 12c104921bb4
Revises: 682820f2c80d
Create Date: 2021-04-16 13:24:10.354828

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "12c104921bb4"
down_revision = "682820f2c80d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("force_delete", sa.Boolean(), server_default=sa.schema.DefaultClause("0"), nullable=False),
        schema="auth",
    )


def downgrade():
    op.drop_column("user", "force_delete", schema="auth")
