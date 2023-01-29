"""Create address table

Revision ID: 50547fef914c
Revises: 1944ef5f8de8
Create Date: 2023-01-13 14:37:55.039626

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '50547fef914c'
down_revision = '1944ef5f8de8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "address",
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('address1', sa.String(), nullable=False),
        sa.Column('address2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('postalcode', sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('address')
