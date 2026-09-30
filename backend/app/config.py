"""Application configuration loaded from environment variables.

Secrets fail closed: the app refuses to start with the placeholder values
unless `EXPLORERS_ALLOW_INSECURE=true` is explicitly set for local development.
"""
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database provider selection ───────────────────────────────────────────
    # "mysql"    → the MySQL-compatible database (MySQL 8 / MariaDB / TiDB).
    # "supabase" → the Supabase-hosted PostgreSQL database.
    #
    # There is no automatic fallback: the selected provider is the only one
    # the application will ever query.
    database_provider: str = Field(
        default="supabase",
        validation_alias=AliasChoices("DATABASE_PROVIDER", "DB_PROVIDER"),
    )

    # PostgreSQL connection string, used when DATABASE_PROVIDER=supabase.
    # Retained so Supabase can be reactivated without any code change.
    database_url: str = ""

    # MySQL connection details, used when DATABASE_PROVIDER=mysql. Kept as
    # discrete variables so a password containing @ : / ? # & cannot corrupt
    # the connection URL. Set MYSQL_URL instead if you prefer a single URL.
    mysql_host: str = ""
    mysql_port: int = 3306
    mysql_database: str = ""
    mysql_user: str = ""
    mysql_password: str = ""
    mysql_url: str = ""
    # "verify-ca" verifies the server certificate against MYSQL_SSL_CA.
    # "verify-full" additionally checks the certificate hostname. This is the
    # default so hostname verification is never silently omitted.
    # Unverified TLS is rejected at startup by design.
    mysql_ssl_mode: str = "verify-full"
    mysql_ssl_ca: str = ""

    # Connection pool sizing. Defaults suit TiDB Cloud / MySQL 8; lower
    # MYSQL_POOL_SIZE if your host limits concurrent connections.
    db_pool_size: int = 10
    db_max_overflow: int = 20
    mysql_pool_size: int | None = None
    mysql_max_overflow: int | None = None
    mysql_pool_recycle: int | None = None

    # Shared secret used by the admin UI to authenticate admin operations
    # (`X-ADMIN-KEY` header). Keep in sync with the admin area deployment.
    admin_api_key: str = "change-me-admin-key"

    # Security used to sign customer session tokens. MUST be a long random
    # value kept secret from the frontend. Never ship the placeholder.
    secret_key: str = "change-me-customer-secret"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # Local development uses HTTP; production must set COOKIE_SECURE=true.
    cookie_secure: bool = False

    # Google OAuth (server-driven "Sign in with Google"). Leave blank to disable
    # the Google login flow entirely; the /api/auth/google endpoints then return 503.
    google_client_id: str = ""
    google_client_secret: str = ""
    # Callback route must exactly match the "Authorized redirect URIs" configured
    # in the Google Cloud Console OAuth client.
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    # Where the browser lands after a successful (or failed) Google sign-in.
    google_return_url: str = "http://localhost:3000"

    # Environment name: "development" | "production" | "staging"
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "EXPLORERS_ENV"),
    )

    # API Documentation (Swagger UI /docs, ReDoc /redoc, OpenAPI /openapi.json)
    # Defaults to enabled in development, disabled in production unless DOCS_ENABLED=true.
    docs_enabled: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("DOCS_ENABLED", "ENABLE_DOCS"),
    )

    # CORS origins — include both local hostnames used during development.
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3100",
        "https://www.explorerschoice.online",
        "https://explorerschoice.online",
    ]

    # Allow browser origins served from any localhost or private-LAN address on
    # a dev port, so devices on the same network can log in against this backend.
    # Automatically disabled in production environment.
    cors_origin_regex: str | None = (
        r"http://(?:localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):\d{1,5}"
    )

    # Local development escape hatch: allows the placeholder secrets above.
    allow_insecure_defaults: bool = Field(
        default=False,
        validation_alias=AliasChoices("EXPLORERS_ALLOW_INSECURE", "ALLOW_INSECURE_DEFAULTS"),
    )

    # Email notification configuration
    admin_notification_email: str = Field(
        default="infoexplorerschoice@gmail.com",
        validation_alias=AliasChoices("ADMIN_NOTIFICATION_EMAIL", "NOTIFICATION_EMAIL", "SMTP_TO_EMAIL"),
    )
    smtp_host: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_HOST", "MAIL_HOST"),
    )
    smtp_port: int = Field(
        default=587,
        validation_alias=AliasChoices("SMTP_PORT", "MAIL_PORT"),
    )
    smtp_username: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER", "MAIL_USERNAME", "MAIL_USER"),
    )
    smtp_password: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_PASSWORD", "SMTP_PASS", "MAIL_PASSWORD", "MAIL_PASS"),
    )
    smtp_from_email: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_FROM_EMAIL", "MAIL_FROM_EMAIL", "MAIL_FROM"),
    )
    smtp_from_name: str = Field(
        default="Explorers Choice",
        validation_alias=AliasChoices("SMTP_FROM_NAME", "MAIL_FROM_NAME"),
    )
    smtp_use_tls: bool = Field(
        default=True,
        validation_alias=AliasChoices("SMTP_USE_TLS", "SMTP_TLS", "MAIL_TLS"),
    )
    smtp_use_ssl: bool = Field(
        default=False,
        validation_alias=AliasChoices("SMTP_USE_SSL", "SMTP_SSL", "MAIL_SSL"),
    )

    # Railway / Train API configuration
    railway_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("RAILWAY_API_KEY", "RAPIDAPI_KEY", "TRAIN_API_KEY"),
    )
    railway_api_host: str = Field(
        default="irctc1.p.rapidapi.com",
        validation_alias=AliasChoices("RAILWAY_API_HOST", "RAPIDAPI_HOST"),
    )
    railway_api_url: str = Field(
        default="https://irctc1.p.rapidapi.com",
        validation_alias=AliasChoices("RAILWAY_API_URL", "TRAIN_API_BASE_URL"),
    )

    @property
    def active_provider(self) -> str:
        return (self.database_provider or "").strip().lower()

    @property
    def is_mysql(self) -> bool:
        return self.active_provider == "mysql"

    @property
    def is_supabase(self) -> bool:
        return self.active_provider == "supabase"

    @model_validator(mode="after")
    def _guard_placeholder_secrets(self) -> "Settings":
        provider = self.active_provider
        if provider not in ("mysql", "supabase"):
            raise ValueError(
                f"DATABASE_PROVIDER={provider!r} is not supported. "
                "Use 'mysql' or 'supabase'."
            )

        if provider == "mysql":
            # Only the active provider's settings are required. The Supabase
            # DATABASE_URL stays untouched and unvalidated so Supabase can be
            # reactivated later without first repairing its credentials.
            if not self.mysql_url.strip():
                for field in ("mysql_host", "mysql_database", "mysql_user", "mysql_password"):
                    if not getattr(self, field).strip():
                        raise ValueError(
                            f"DATABASE_PROVIDER=mysql requires {field.upper()} "
                            "in backend/.env (or MYSQL_URL instead of those four)."
                        )
            mode = (self.mysql_ssl_mode or "").strip().lower()
            if mode not in ("verify-ca", "verify-full"):
                raise ValueError(
                    f"MYSQL_SSL_MODE={mode!r} is not permitted. Use 'verify-ca' or "
                    "'verify-full' so the server certificate is always verified."
                )
        else:
            if not self.database_url.strip():
                raise ValueError(
                    "DATABASE_PROVIDER=supabase requires DATABASE_URL to point at the "
                    "shared application database."
                )
            if self.database_url.startswith("sqlite"):
                raise ValueError("SQLite is no longer supported. Please use PostgreSQL or MySQL.")

        if (
            not self.secret_key
            or self.secret_key == "change-me-customer-secret"
            or self.secret_key.startswith("change-me")
        ):
            if not self.allow_insecure_defaults:
                raise ValueError(
                    "SECRET_KEY must be set to a strong random value. "
                    "For local development only, set EXPLORERS_ALLOW_INSECURE=true."
                )
        if not self.admin_api_key or self.admin_api_key == "change-me-admin-key":
            if not self.allow_insecure_defaults:
                raise ValueError(
                    "ADMIN_API_KEY must be set to a strong random value. "
                    "For local development only, set EXPLORERS_ALLOW_INSECURE=true."
                )

        # Default docs_enabled based on environment if not explicitly configured
        if self.docs_enabled is None:
            self.docs_enabled = self.environment.lower() not in ("production", "prod")

        # In production, disable LAN regex matching for CORS and enforce secure cookies
        if self.environment.lower() in ("production", "prod"):
            self.cors_origin_regex = None
            if not self.cookie_secure:
                raise ValueError(
                    "COOKIE_SECURE must be true in production to prevent cleartext session cookies."
                )

        for origin in ("https://www.explorerschoice.online", "https://explorerschoice.online"):
            if origin not in self.cors_origins:
                self.cors_origins.append(origin)
        return self


settings = Settings()