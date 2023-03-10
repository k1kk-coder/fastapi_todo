"""create address_id to users

Revision ID: 9b07f851e687
Revises: 50547fef914c
Create Date: 2023-01-13 14:49:35.648618

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '9b07f851e687'
down_revision = '50547fef914c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'address_users_fk', source_table='users', referent_table='address',
        local_cols=['address_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('address_users_fk', table_name='users')
    op.drop_column('users', 'address_id')
