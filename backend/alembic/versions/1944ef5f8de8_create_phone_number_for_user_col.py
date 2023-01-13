"""create phone number for user col

Revision ID: 1944ef5f8de8
Revises: 
Create Date: 2023-01-13 14:21:33.417343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1944ef5f8de8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column(
        'users', 'phone_number'
    )
