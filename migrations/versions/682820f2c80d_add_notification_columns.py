"""migrations/manual_scripts/add_notification_column.sql

Revision ID: 682820f2c80d
Revises: 85a1d35fedb7
Create Date: 2020-09-29 14:46:46.626168

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "682820f2c80d"
down_revision = "85a1d35fedb7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(table_name="user", schema="auth") as batch_op:
        batch_op.add_column(sa.Column("first_notification", sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column("second_notification", sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column("third_notification", sa.DateTime, nullable=True))


def downgrade():
    with op.batch_alter_table(table_name="user", schema="auth") as batch_op:
        batch_op.drop_column("first_notification")
        batch_op.drop_column("second_notification")
        batch_op.drop_column("third_notification")
