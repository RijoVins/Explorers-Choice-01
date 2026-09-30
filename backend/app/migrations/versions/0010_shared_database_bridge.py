"""align local migration history with the shared database

Revision ID: 0010_shared_database_bridge
Revises: 0010
Create Date: 2026-09-21
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0010_shared_database_bridge"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The shared database is already stamped at 0010; this revision preserves
    # that history without repeating an operation that has already been applied.
    pass


def downgrade() -> None:
    pass