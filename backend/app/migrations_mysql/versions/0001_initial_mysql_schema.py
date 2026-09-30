"""MySQL initial schema for the Explorers Choice application.

Generated from the ORM metadata in ``app/models.py`` so this schema matches what
the application actually queries. Deliberate PostgreSQL -> MySQL differences:

    JSONB / JSON      -> my.JSON()
    timestamptz       -> my.DATETIME(fsp=6) holding naive UTC, re-attached as UTC on
                         read by app.db.types.UTCDateTime
    TEXT (unbounded)  -> my.LONGTEXT(); MySQL TEXT caps at 64 KiB and errors
    boolean           -> my.BOOLEAN (TINYINT(1)) with 0/1 defaults
    string defaults   -> quoted literals, e.g. DEFAULT '' / DEFAULT 'CUSTOMER'
    TEXT / JSON       -> no server default: TiDB rejects DEFAULT on BLOB/TEXT/JSON
                         columns; the ORM supplies these values in Python
    timestamps        -> DEFAULT CURRENT_TIMESTAMP(6)

MySQL-only. The PostgreSQL history in ``app/migrations`` is untouched and must
never be run against MySQL.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql as my

revision = "0001_mysql_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('auth_provider', sa.String(20), nullable=False, server_default='EMAIL'),
        sa.Column('provider_account_id', sa.String(160), nullable=True),
        sa.Column('full_name', sa.String(160), nullable=False, server_default=''),
        sa.Column('phone', sa.String(60), nullable=False, server_default=''),
        sa.Column('country', sa.String(120), nullable=False, server_default=''),
        sa.Column('role', sa.String(32), nullable=False, server_default='CUSTOMER'),
        sa.Column('requested_role', sa.String(32), nullable=True),
        sa.Column('is_staff', my.BOOLEAN, nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('token_version', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_staff', 'users', ['is_staff'], unique=False)
    op.create_index('ix_users_provider_account_id', 'users', ['provider_account_id'], unique=False)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)

    op.create_table(
        'destinations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('slug', sa.String(180), nullable=False),
        sa.Column('country', sa.String(120), nullable=False),
        sa.Column('region', sa.String(120), nullable=False, server_default=''),
        sa.Column('short_description', my.LONGTEXT(), nullable=False),
        sa.Column('description', my.LONGTEXT(), nullable=False),
        sa.Column('hero_image', sa.String(500), nullable=False, server_default=''),
        sa.Column('gallery', my.JSON(), nullable=False),
        sa.Column('best_time', sa.String(160), nullable=False, server_default=''),
        sa.Column('recommended_duration', sa.String(120), nullable=False, server_default=''),
        sa.Column('highlights', my.JSON(), nullable=False),
        sa.Column('things_to_do', my.JSON(), nullable=False),
        sa.Column('travel_information', my.JSON(), nullable=False),
        sa.Column('is_featured', my.BOOLEAN, nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
    )
    op.create_index('ix_destinations_slug', 'destinations', ['slug'], unique=True)

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', my.DATETIME(fsp=6), nullable=False),
        sa.Column('used_at', my.DATETIME(fsp=6), nullable=True),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'], unique=True)
    op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'], unique=False)

    op.create_table(
        'packages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('destination_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(220), nullable=False),
        sa.Column('short_description', my.LONGTEXT(), nullable=False),
        sa.Column('description', my.LONGTEXT(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('duration_nights', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('starting_price', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('hero_image', sa.String(500), nullable=False, server_default=''),
        sa.Column('gallery', my.JSON(), nullable=False),
        sa.Column('highlights', my.JSON(), nullable=False),
        sa.Column('included', my.JSON(), nullable=False),
        sa.Column('excluded', my.JSON(), nullable=False),
        sa.Column('accommodation_summary', my.LONGTEXT(), nullable=False),
        sa.Column('transportation_summary', my.LONGTEXT(), nullable=False),
        sa.Column('meal_summary', my.LONGTEXT(), nullable=False),
        sa.Column('cancellation_policy', my.LONGTEXT(), nullable=False),
        sa.Column('important_information', my.JSON(), nullable=False),
        sa.Column('booking_mode', sa.String(32), nullable=False, server_default='REQUEST_ONLY'),
        sa.Column('is_featured', my.BOOLEAN, nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_packages_destination_id', 'packages', ['destination_id'], unique=False)
    op.create_index('ix_packages_slug', 'packages', ['slug'], unique=True)

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(254), nullable=False, server_default=''),
        sa.Column('action', sa.String(120), nullable=False),
        sa.Column('entity', sa.String(80), nullable=False),
        sa.Column('entity_id', sa.String(64), nullable=False, server_default=''),
        sa.Column('details', my.LONGTEXT(), nullable=False),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)

    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('key', sa.String(120), nullable=False),
        sa.Column('value', my.JSON(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_settings_key', 'settings', ['key'], unique=True)

    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(220), nullable=False),
        sa.Column('location', sa.String(160), nullable=False, server_default=''),
        sa.Column('destination', sa.String(160), nullable=False, server_default=''),
        sa.Column('tagline', sa.String(240), nullable=False, server_default=''),
        sa.Column('description', my.LONGTEXT(), nullable=False),
        sa.Column('image', sa.String(500), nullable=False, server_default=''),
        sa.Column('price_per_night', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('amenities', my.JSON(), nullable=False),
        sa.Column('highlights', my.JSON(), nullable=False),
        sa.Column('is_published', my.BOOLEAN, nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_hotels_owner_id', 'hotels', ['owner_id'], unique=False)
    op.create_index('ix_hotels_slug', 'hotels', ['slug'], unique=True)

    op.create_table(
        'train_bookings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_reference', sa.String(32), nullable=False),
        sa.Column('pnr_number', sa.String(10), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('train_number', sa.String(10), nullable=False),
        sa.Column('train_name', sa.String(160), nullable=False),
        sa.Column('from_station_code', sa.String(10), nullable=False),
        sa.Column('from_station_name', sa.String(120), nullable=False),
        sa.Column('to_station_code', sa.String(10), nullable=False),
        sa.Column('to_station_name', sa.String(120), nullable=False),
        sa.Column('journey_date', sa.Date(), nullable=False),
        sa.Column('departure_time', sa.String(10), nullable=False),
        sa.Column('arrival_time', sa.String(10), nullable=False),
        sa.Column('duration', sa.String(30), nullable=False, server_default=''),
        sa.Column('travel_class', sa.String(10), nullable=False),
        sa.Column('quota', sa.String(30), nullable=False, server_default='GENERAL'),
        sa.Column('passengers', my.JSON(), nullable=False),
        sa.Column('contact_name', sa.String(160), nullable=False),
        sa.Column('contact_email', sa.String(254), nullable=False),
        sa.Column('contact_phone', sa.String(60), nullable=False),
        sa.Column('base_fare', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('convenience_fee', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('gst', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('status', sa.String(32), nullable=False, server_default='CONFIRMED'),
        sa.Column('idempotency_key', sa.String(64), nullable=True),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_train_bookings_booking_reference', 'train_bookings', ['booking_reference'], unique=True)
    op.create_index('ix_train_bookings_contact_email', 'train_bookings', ['contact_email'], unique=False)
    op.create_index('ix_train_bookings_created_at', 'train_bookings', ['created_at'], unique=False)
    op.create_index('ix_train_bookings_from_station_code', 'train_bookings', ['from_station_code'], unique=False)
    op.create_index('ix_train_bookings_idempotency_key', 'train_bookings', ['idempotency_key'], unique=True)
    op.create_index('ix_train_bookings_journey_date', 'train_bookings', ['journey_date'], unique=False)
    op.create_index('ix_train_bookings_pnr_number', 'train_bookings', ['pnr_number'], unique=True)
    op.create_index('ix_train_bookings_status', 'train_bookings', ['status'], unique=False)
    op.create_index('ix_train_bookings_to_station_code', 'train_bookings', ['to_station_code'], unique=False)
    op.create_index('ix_train_bookings_train_number', 'train_bookings', ['train_number'], unique=False)
    op.create_index('ix_train_bookings_user_id', 'train_bookings', ['user_id'], unique=False)

    op.create_table(
        'cab_bookings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_reference', sa.String(32), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('trip_type', sa.String(32), nullable=False),
        sa.Column('cab_type', sa.String(40), nullable=False),
        sa.Column('pickup_location', sa.String(300), nullable=False),
        sa.Column('drop_location', sa.String(300), nullable=False),
        sa.Column('pickup_date', sa.Date(), nullable=False),
        sa.Column('pickup_time', sa.String(5), nullable=False),
        sa.Column('distance_kms', sa.Numeric(8, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('passengers', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('full_name', sa.String(160), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('phone', sa.String(60), nullable=False),
        sa.Column('special_requirements', my.LONGTEXT(), nullable=False),
        sa.Column('base_fare', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('convenience_fee', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('gst', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('status', sa.String(32), nullable=False, server_default='PENDING_CONFIRMATION'),
        sa.Column('idempotency_key', sa.String(64), nullable=True),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_cab_bookings_booking_reference', 'cab_bookings', ['booking_reference'], unique=True)
    op.create_index('ix_cab_bookings_created_at', 'cab_bookings', ['created_at'], unique=False)
    op.create_index('ix_cab_bookings_email', 'cab_bookings', ['email'], unique=False)
    op.create_index('ix_cab_bookings_idempotency_key', 'cab_bookings', ['idempotency_key'], unique=True)
    op.create_index('ix_cab_bookings_pickup_date', 'cab_bookings', ['pickup_date'], unique=False)
    op.create_index('ix_cab_bookings_status', 'cab_bookings', ['status'], unique=False)
    op.create_index('ix_cab_bookings_trip_type', 'cab_bookings', ['trip_type'], unique=False)
    op.create_index('ix_cab_bookings_user_id', 'cab_bookings', ['user_id'], unique=False)

    op.create_table(
        'itinerary_days',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(240), nullable=False, server_default=''),
        sa.Column('description', my.LONGTEXT(), nullable=False),
        sa.Column('activities', my.JSON(), nullable=False),
        sa.Column('meals', sa.String(160), nullable=False, server_default=''),
        sa.Column('accommodation', sa.String(240), nullable=False, server_default=''),
        sa.Column('transportation', sa.String(240), nullable=False, server_default=''),
        sa.UniqueConstraint('package_id', 'day_number', name='uq_itinerary_day_package_number'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_itinerary_days_package_id', 'itinerary_days', ['package_id'], unique=False)

    op.create_table(
        'package_faqs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(320), nullable=False),
        sa.Column('answer', my.LONGTEXT(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_package_faqs_package_id', 'package_faqs', ['package_id'], unique=False)

    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_reference', sa.String(32), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.Column('travel_date', sa.Date(), nullable=False),
        sa.Column('adults', sa.Integer(), nullable=False),
        sa.Column('children', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('infants', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('departure_information', my.LONGTEXT(), nullable=False),
        sa.Column('full_name', sa.String(160), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('phone', sa.String(60), nullable=False),
        sa.Column('country', sa.String(120), nullable=False),
        sa.Column('special_requirements', my.LONGTEXT(), nullable=False),
        sa.Column('notes', my.LONGTEXT(), nullable=False),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False),
        sa.Column('taxes', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('total', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='PENDING_CONFIRMATION'),
        sa.Column('payment_status', sa.String(32), nullable=False, server_default='NOT_REQUIRED'),
        sa.Column('package_name', sa.String(200), nullable=False),
        sa.Column('destination_name', sa.String(160), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('booking_mode', sa.String(32), nullable=False),
        sa.Column('idempotency_key', sa.String(64), nullable=True),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_bookings_booking_reference', 'bookings', ['booking_reference'], unique=True)
    op.create_index('ix_bookings_created_at', 'bookings', ['created_at'], unique=False)
    op.create_index('ix_bookings_email', 'bookings', ['email'], unique=False)
    op.create_index('ix_bookings_idempotency_key', 'bookings', ['idempotency_key'], unique=True)
    op.create_index('ix_bookings_package_id', 'bookings', ['package_id'], unique=False)
    op.create_index('ix_bookings_status', 'bookings', ['status'], unique=False)
    op.create_index('ix_bookings_user_id', 'bookings', ['user_id'], unique=False)

    op.create_table(
        'enquiries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('customer_name', sa.String(160), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('phone', sa.String(60), nullable=False, server_default=''),
        sa.Column('country', sa.String(120), nullable=False, server_default=''),
        sa.Column('destination_interest', sa.String(160), nullable=False, server_default=''),
        sa.Column('package_id', sa.Integer(), nullable=True),
        sa.Column('package_name', sa.String(200), nullable=False, server_default=''),
        sa.Column('travel_date_from', sa.Date(), nullable=True),
        sa.Column('travel_date_to', sa.Date(), nullable=True),
        sa.Column('travellers', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('budget', sa.String(120), nullable=False, server_default=''),
        sa.Column('message', my.LONGTEXT(), nullable=False),
        sa.Column('notes', my.LONGTEXT(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='NEW'),
        sa.Column('assigned_staff_id', sa.Integer(), nullable=True),
        sa.Column('last_contact_at', my.DATETIME(fsp=6), nullable=True),
        sa.Column('next_action', sa.String(320), nullable=False, server_default=''),
        sa.Column('next_action_at', sa.Date(), nullable=True),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['assigned_staff_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_enquiries_assigned_staff_id', 'enquiries', ['assigned_staff_id'], unique=False)
    op.create_index('ix_enquiries_created_at', 'enquiries', ['created_at'], unique=False)
    op.create_index('ix_enquiries_email', 'enquiries', ['email'], unique=False)
    op.create_index('ix_enquiries_status', 'enquiries', ['status'], unique=False)

    op.create_table(
        'customer_stories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('customer_name', sa.String(160), nullable=False),
        sa.Column('destination', sa.String(160), nullable=False, server_default=''),
        sa.Column('package_id', sa.Integer(), nullable=True),
        sa.Column('package_name', sa.String(200), nullable=False, server_default=''),
        sa.Column('story', my.LONGTEXT(), nullable=False),
        sa.Column('photos', my.JSON(), nullable=False),
        sa.Column('travel_date', sa.Date(), nullable=True),
        sa.Column('is_featured', my.BOOLEAN, nullable=False, server_default=sa.text('0')),
        sa.Column('is_published', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='SET NULL'),
    )

    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('code', sa.String(40), nullable=False, server_default=''),
        sa.Column('description', my.LONGTEXT(), nullable=False),
        sa.Column('discount_type', sa.String(16), nullable=False, server_default='PERCENT'),
        sa.Column('discount_value', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('package_id', sa.Integer(), nullable=True),
        sa.Column('package_name', sa.String(200), nullable=False, server_default=''),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('is_active', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_offers_code', 'offers', ['code'], unique=False)

    op.create_table(
        'booking_travellers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('traveller_type', sa.String(16), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_booking_travellers_booking_id', 'booking_travellers', ['booking_id'], unique=False)

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='PENDING'),
        sa.Column('provider', sa.String(64), nullable=False, server_default=''),
        sa.Column('provider_reference', sa.String(160), nullable=False, server_default=''),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.Column('updated_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.CheckConstraint('amount >= 0', name='ck_payment_amount_non_negative'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_payments_booking_id', 'payments', ['booking_id'], unique=False)

    op.create_table(
        'booking_documents',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(40), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('is_secure', my.BOOLEAN, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_booking_documents_booking_id', 'booking_documents', ['booking_id'], unique=False)

    op.create_table(
        'booking_notes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('body', my.LONGTEXT(), nullable=False),
        sa.Column('created_at', my.DATETIME(fsp=6), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP(6)')),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_booking_notes_booking_id', 'booking_notes', ['booking_id'], unique=False)


def downgrade() -> None():
    op.drop_table('booking_notes')
    op.drop_table('booking_documents')
    op.drop_table('payments')
    op.drop_table('booking_travellers')
    op.drop_table('offers')
    op.drop_table('customer_stories')
    op.drop_table('enquiries')
    op.drop_table('bookings')
    op.drop_table('package_faqs')
    op.drop_table('itinerary_days')
    op.drop_table('cab_bookings')
    op.drop_table('train_bookings')
    op.drop_table('hotels')
    op.drop_table('settings')
    op.drop_table('audit_logs')
    op.drop_table('packages')
    op.drop_table('password_reset_tokens')
    op.drop_table('destinations')
    op.drop_table('users')
