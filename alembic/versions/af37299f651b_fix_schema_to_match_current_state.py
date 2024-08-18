"""Migration to update tables and manage constraints

Revision ID: <combined_revision_id>
Revises: <previous_revision_id>
Create Date: <current_date>
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af37299f651b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Create temporary tables with foreign key constraints ###
    op.create_table(
        'temp_participant_groups',
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('participant_id', 'group_id'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE')
    )

    op.create_table(
        'temp_team_participants',
        sa.Column('team_name', sa.String(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('team_name', 'group_id', 'participant_id'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE')
    )

    # ### Copy data from old tables to new tables ###
    op.execute("""
    INSERT INTO temp_participant_groups (participant_id, group_id)
    SELECT participant_id, group_id FROM participant_groups;
    """)

    op.execute("""
    INSERT INTO temp_team_participants (team_name, group_id, participant_id)
    SELECT team_name, group_id, participant_id FROM team_participants;
    """)

    # ### Drop old tables (including constraints) ###
    op.drop_table('participant_groups')
    op.drop_table('team_participants')

    # ### Drop tables that are no longer needed ###
    op.drop_table('groups')
    op.drop_table('teams')

    # ### Rename temporary tables ###
    op.rename_table('temp_participant_groups', 'participant_groups')
    op.rename_table('temp_team_participants', 'team_participants')