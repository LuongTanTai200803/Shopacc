"""Manually add default to coin column

Revision ID: 9e41ccf80718
Revises: 
Create Date: 2025-05-27 22:15:41.506033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e41ccf80718'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('users', 'coin', server_default='0')


def downgrade():
    op.alter_column('users', 'coin', server_default=None)
