"""Register the database revision already applied to the shared database."""

from typing import Sequence, Union


from alembic import op


revision: str = "0011_database_revision_marker"
down_revision: Union[str, None] = "0010_shared_database_bridge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass