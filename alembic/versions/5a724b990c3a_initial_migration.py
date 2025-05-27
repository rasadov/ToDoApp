"""initial migration

Revision ID: 5a724b990c3a
Revises: 
Create Date: 2025-05-28 00:38:13.432988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a724b990c3a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('first_name', sa.VARCHAR(), nullable=False),
        sa.Column('last_name', sa.VARCHAR(), nullable=False),
        sa.Column('username', sa.VARCHAR(), nullable=False),
        sa.Column('password', sa.VARCHAR(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.Column('description', sa.VARCHAR(), nullable=True),
        sa.Column('status', sa.VARCHAR(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('tasks')
    op.drop_table('users')
