"""add seasons

Revision ID: 7c1d4e2a9b30
Revises: 2e63c85b8716
Create Date: 2026-10-24 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c1d4e2a9b30'
down_revision: Union[str, Sequence[str], None] = '2e63c85b8716'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('seasons',
    sa.Column('season', sa.String(), nullable=False),
    sa.Column('first_match_date', sa.DateTime(), nullable=False),
    sa.Column('last_match_date', sa.DateTime(), nullable=False),
    sa.Column('ended', sa.Boolean(), nullable=False),
    sa.Column('teams', sa.ARRAY(sa.String()), nullable=False),
    sa.PrimaryKeyConstraint('season')
    )


def downgrade() -> None:
    op.drop_table('seasons')
