"""add new column apt_num to address

Revision ID: dfee98986116
Revises: 9b07f851e687
Create Date: 2023-01-13 16:15:32.280593

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'dfee98986116'
down_revision = '9b07f851e687'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column(
        'apt_num',
        sa.String(50),
        nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
