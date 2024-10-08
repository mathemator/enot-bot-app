"""Initial migration

Revision ID: dd235c8088d8
Revises: 
Create Date: 2024-08-18 09:25:38.379429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd235c8088d8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('participants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('participant_groups',
    sa.Column('participant_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], name='fk_participant_groups_participant_id'),
    sa.PrimaryKeyConstraint('participant_id', 'group_id', name='pk_participant_groups')
    )
    op.create_table('team_participants',
    sa.Column('team_name', sa.String(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('participant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], name='fk_team_participants_participant_id'),
    sa.PrimaryKeyConstraint('team_name', 'group_id', 'participant_id', name='team_participants')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_participants')
    op.drop_table('participant_groups')
    op.drop_table('participants')
    # ### end Alembic commands ###
