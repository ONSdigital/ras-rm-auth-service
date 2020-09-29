"""migrations/manual_scripts/add_notification_column.sql

Revision ID: 682820f2c80d
Revises: 85a1d35fedb7
Create Date: 2020-09-29 14:46:46.626168

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '682820f2c80d'
down_revision = '85a1d35fedb7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(table_name='user', schema="auth") as batch_op:
        batch_op.add_column(sa.Column('due_deletion_first_notification_date', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('due_deletion_second_notification_date', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('due_deletion_third_notification_date', sa.DateTime, nullable=True))


def downgrade():
    with op.batch_alter_table(table_name='user', schema="auth") as batch_op:
        batch_op.drop_column('due_deletion_first_notification_date')
        batch_op.drop_column('due_deletion_second_notification_date')
        batch_op.drop_column('due_deletion_third_notification_date')
