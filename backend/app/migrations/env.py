import os
import sys

# Ensure the backend project root is on the import path before importing the app.
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from sqlalchemy import pool  # noqa: E402
from alembic import context  # noqa: E402

from app.database import Base  # noqa: E402
import app.models  # noqa: E402, F401 — registers models with Base.metadata

# This directory contains the legacy PostgreSQL migration history.
# It is kept for reference only and should not be run.
# MySQL schema is managed via the migrations_mysql/ directory.
raise RuntimeError(
    "The app/migrations/ directory contains the legacy PostgreSQL migration history "
    "and is not used. Use app/migrations_mysql/ instead."
)
