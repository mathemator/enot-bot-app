"""Recreate tables with constraints

Revision ID: <new_revision_id>
Revises: <previous_revision_id>
Create Date: <date>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '67ab030f6324'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'temp_participants',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_participants')
    )

        # 2. Создание временных таблиц participant_groups и team_participants с правильными именами внешних ключей
    op.create_table(
        'temp_participant_groups',
        sa.Column('participant_id', sa.Integer, sa.ForeignKey('temp_participants.id', name='fk_temp_participant_groups_participant_id'), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('participant_id', 'group_id')
    )

    op.create_table(
        'temp_team_participants',
        sa.Column('team_name', sa.String(50)),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer, sa.ForeignKey('temp_participants.id', name='fk_temp_team_participants_participant_id'), nullable=False),
        sa.PrimaryKeyConstraint('team_name', 'participant_id')
    )

    # 3. Перенос данных из старых таблиц во временные
    op.execute('INSERT INTO temp_participants (id, username, first_name, last_name) SELECT id, username, first_name, last_name FROM participants')
    op.execute('INSERT INTO temp_participant_groups SELECT * FROM participant_groups')
    op.execute('INSERT INTO temp_team_participants SELECT * FROM team_participants')

    # 4. Удаление старых таблиц participant_groups и team_participants
    op.drop_table('participant_groups')
    op.drop_table('team_participants')

    # 5. Удаление старой таблицы participants
    op.drop_table('participants')

    # 6. Переименование временных таблиц в исходные
    op.rename_table('temp_participants', 'participants')
    op.rename_table('temp_participant_groups', 'participant_groups')
    op.rename_table('temp_team_participants', 'team_participants')