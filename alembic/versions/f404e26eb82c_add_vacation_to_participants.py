"""add vacation to participants

Revision ID: f404e26eb82c
Revises: e97305481ca2
Create Date: 2026-01-01 19:47:24.076199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f404e26eb82c'
down_revision = 'e97305481ca2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку vacation, по дефолту False
    op.add_column('participants', sa.Column('vacation', sa.Boolean(), nullable=False, server_default=sa.text('0')))

def downgrade() -> None:
    # Убираем колонку при откате
    op.drop_column('participants', 'vacation')