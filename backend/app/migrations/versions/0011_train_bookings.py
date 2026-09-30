"""add train bookings

Revision ID: 0011
Revises: 0011_database_revision_marker
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011"
down_revision: Union[str, None] = "0011_database_revision_marker"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "train_bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_reference", sa.String(32), nullable=False),
        sa.Column("pnr_number", sa.String(10), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("train_number", sa.String(10), nullable=False),
        sa.Column("train_name", sa.String(160), nullable=False),
        sa.Column("from_station_code", sa.String(10), nullable=False),
        sa.Column("from_station_name", sa.String(120), nullable=False),
        sa.Column("to_station_code", sa.String(10), nullable=False),
        sa.Column("to_station_name", sa.String(120), nullable=False),
        sa.Column("journey_date", sa.Date(), nullable=False),
        sa.Column("departure_time", sa.String(10), nullable=False),
        sa.Column("arrival_time", sa.String(10), nullable=False),
        sa.Column("duration", sa.String(30), nullable=False, server_default=""),
        sa.Column("travel_class", sa.String(10), nullable=False),
        sa.Column("quota", sa.String(30), nullable=False, server_default="GENERAL"),
        sa.Column("passengers", sa.JSON(), nullable=False),
        sa.Column("contact_name", sa.String(160), nullable=False),
        sa.Column("contact_email", sa.String(254), nullable=False),
        sa.Column("contact_phone", sa.String(60), nullable=False),
        sa.Column("base_fare", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("convenience_fee", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("gst", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(32), nullable=False, server_default="CONFIRMED"),
        sa.Column("idempotency_key", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_train_bookings_booking_reference", "train_bookings", ["booking_reference"], unique=True)
    op.create_index("ix_train_bookings_pnr_number", "train_bookings", ["pnr_number"], unique=True)
    op.create_index("ix_train_bookings_user_id", "train_bookings", ["user_id"])
    op.create_index("ix_train_bookings_train_number", "train_bookings", ["train_number"])
    op.create_index("ix_train_bookings_from_station_code", "train_bookings", ["from_station_code"])
    op.create_index("ix_train_bookings_to_station_code", "train_bookings", ["to_station_code"])
    op.create_index("ix_train_bookings_journey_date", "train_bookings", ["journey_date"])
    op.create_index("ix_train_bookings_contact_email", "train_bookings", ["contact_email"])
    op.create_index("ix_train_bookings_status", "train_bookings", ["status"])
    op.create_index("ix_train_bookings_idempotency_key", "train_bookings", ["idempotency_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_train_bookings_idempotency_key", table_name="train_bookings")
    op.drop_index("ix_train_bookings_status", table_name="train_bookings")
    op.drop_index("ix_train_bookings_contact_email", table_name="train_bookings")
    op.drop_index("ix_train_bookings_journey_date", table_name="train_bookings")
    op.drop_index("ix_train_bookings_to_station_code", table_name="train_bookings")
    op.drop_index("ix_train_bookings_from_station_code", table_name="train_bookings")
    op.drop_index("ix_train_bookings_train_number", table_name="train_bookings")
    op.drop_index("ix_train_bookings_user_id", table_name="train_bookings")
    op.drop_index("ix_train_bookings_pnr_number", table_name="train_bookings")
    op.drop_index("ix_train_bookings_booking_reference", table_name="train_bookings")
    op.drop_table("train_bookings")