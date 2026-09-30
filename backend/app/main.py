"""Main FastAPI application for Explorers Choice."""
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import time
import uuid

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError

from .config import settings
from .database import Base, engine, SessionLocal, dispose, provider
from . import models, security

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("explorers")
from .routes import account as account_router
from .routes import admin as admin_router
from .routes import auth as auth_router
from .routes import bookings as bookings_router
from .routes import cabs as cabs_router
from .routes import destinations as destinations_router
from .routes import enquiries as enquiries_router, stories as stories_router
from .routes import hotels as hotels_router
from .routes import oauth as oauth_router
from .routes import packages as packages_router
from .routes import trains as trains_router

def run_startup_migrations():
    """Ensure database schema is up-to-date with Alembic migrations on startup.

    BUG-09: migration failures now raise SystemExit so startup cannot continue
    against an outdated schema.

    This runs ONLY for the Supabase/PostgreSQL provider. When
    ``DATABASE_PROVIDER=mysql`` the MySQL schema is owned outside this
    application, so Alembic is skipped entirely and startup performs a
    read-only connectivity check instead. No table is ever created, altered or
    dropped against MySQL.
    """
    if not provider.run_migrations_on_startup():
        logger.info(
            "DATABASE_PROVIDER=%s: skipping Alembic (schema is managed outside "
            "this application). Verifying connectivity read-only instead.",
            provider.name,
        )
        check_database_connectivity()
        return

    try:
        backend_dir = Path(__file__).resolve().parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        if alembic_ini.exists():
            alembic_cfg = Config(str(alembic_ini))
            alembic_cfg.set_main_option("script_location", str(backend_dir / "app" / "migrations"))
            # alembic uses configparser, which treats % as interpolation unless escaped.
            escaped_url = settings.database_url.replace("%", "%%")
            alembic_cfg.set_main_option("sqlalchemy.url", escaped_url)
            command.upgrade(alembic_cfg, "head")
            logger.info("Database schema verified / upgraded to head successfully.")
        else:
            logger.warning("alembic.ini not found; cannot verify schema.")
    except Exception as exc:
        logger.critical("Database migration failed, refusing to start: %s", exc)
        raise SystemExit(1) from exc


def check_database_connectivity():
    """Read-only startup probe. Issues SELECT 1 and nothing else.

    Never falls back to the other provider: if the selected database is
    unreachable the process refuses to start.
    """
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connectivity OK (provider=%s).", provider.name)
    except Exception as exc:
        logger.critical(
            "Database unreachable (provider=%s), refusing to start: %s",
            provider.name, exc,
        )
        raise SystemExit(1) from exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify or migrate the selected database
    run_startup_migrations()
    logger.info(
        "Started with DATABASE_PROVIDER=%s (dialect=%s).",
        provider.name, engine.dialect.name,
    )
    yield
    # Shutdown: return pooled connections cleanly
    dispose()


app = FastAPI(
    title="Explorers Choice API",
    description="Destination, package, itinerary, booking and account management for Explorers Choice.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """FK/unique violations surface as 409 instead of a raw 500."""
    logger.warning("IntegrityError on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": "This record is referenced by other data and cannot be deleted or duplicated."},
    )


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    """The selected database is unreachable.

    The request fails with 503. The application never retries against the
    other provider, because silently switching backends mid-request would
    read or write the wrong database.
    """
    logger.error("OperationalError on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database temporarily unavailable. Please try again shortly.",
            "provider": provider.name,
        },
    )


@app.exception_handler(DBAPIError)
async def dbapi_error_handler(request: Request, exc: DBAPIError):
    """Catch-all for driver-level database errors (no fallback, no leakage)."""
    logger.error("DBAPIError on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database error while processing the request.",
            "provider": provider.name,
        },
    )


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.monotonic()
    response = await call_next(request)
    elapsed_ms = round((time.monotonic() - start) * 1000, 1)
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    logger.info(
        "%s %s -> %s (%sms, id=%s)",
        request.method, request.url.path, response.status_code, elapsed_ms, request_id,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
    """CSRF guard for cookie-authenticated state-changing requests.

    If a request carries a session cookie and uses an unsafe method
    (POST, PUT, PATCH, DELETE), verify that Origin (or Referer)
    matches an allowed frontend origin.
    """
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        has_session = security.COOKIE_NAME in request.cookies
        if has_session:
            origin = request.headers.get("origin") or request.headers.get("referer")
            if not security.is_allowed_origin(origin):
                logger.warning(
                    "CSRF blocked: %s %s with Origin=%s, Referer=%s",
                    request.method, request.url.path,
                    request.headers.get("origin"), request.headers.get("referer"),
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF check failed: invalid or missing request origin."},
                )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(destinations_router.router, prefix="/api/destinations", tags=["destinations"])
app.include_router(packages_router.router, prefix="/api/packages", tags=["packages"])
app.include_router(bookings_router.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(oauth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(account_router.router, prefix="/api/account", tags=["account"])
app.include_router(hotels_router.router, prefix="/api/hotels", tags=["hotels"])
app.include_router(trains_router.router, prefix="/api/trains", tags=["trains"])
app.include_router(cabs_router.router, prefix="/api/cabs", tags=["cabs"])
app.include_router(hotels_router.owner_router, prefix="/api/hotel-owner", tags=["hotel owner"])
app.include_router(hotels_router.admin_router, prefix="/api/admin", tags=["admin hotels"])
app.include_router(destinations_router.admin_router, prefix="/api/admin", tags=["admin destinations"])
app.include_router(packages_router.admin_router, prefix="/api/admin", tags=["admin packages"])
app.include_router(bookings_router.admin_router, prefix="/api/admin", tags=["admin bookings"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["admin operations"])
app.include_router(enquiries_router.router, prefix="/api/enquiries", tags=["public enquiries"])
app.include_router(stories_router.router, prefix="/api", tags=["public stories"])

@app.get("/api/health", tags=["system"])
def health():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "provider": provider.name}
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": "Database unreachable", "provider": provider.name},
        )