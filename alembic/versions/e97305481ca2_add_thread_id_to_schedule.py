"""add thread_id to schedule

Revision ID: e97305481ca2
Revises: 0926f82f4dfe
Create Date: 2024-10-20 20:16:22.107766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e97305481ca2'
down_revision: Union[str, None] = '0926f82f4dfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scheduled_tasks', sa.Column('thread_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scheduled_tasks', 'thread_id')
    # ### end Alembic commands ###
