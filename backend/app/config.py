"""Application configuration loaded from environment variables.

The only supported database backend is MySQL (including TiDB Cloud).

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

    # ── Database ──────────────────────────────────────────────────────────────
    # Only "mysql" is supported. This value is hardcoded and not configurable.
    database_provider: str = "mysql"

    # MySQL connection details. Kept as discrete variables so a password
    # containing @ : / ? # & cannot corrupt the connection URL.
    # Set MYSQL_URL instead if you prefer a single connection string.
    mysql_host: str = ""
    mysql_port: int = 3306
    mysql_database: str = ""
    mysql_user: str = ""
    mysql_password: str = ""
    mysql_url: str = ""
    # "verify-ca" verifies the server certificate against MYSQL_SSL_CA.
    # "verify-full" additionally checks the certificate hostname.
    mysql_ssl_mode: str = "verify-ca"
    mysql_ssl_ca: str = ""

    # Connection pool sizing. Defaults suit TiDB Cloud / MySQL 8.
    mysql_pool_size: int | None = None
    mysql_max_overflow: int | None = None
    mysql_pool_recycle: int | None = None

    # ── Admin & Security ──────────────────────────────────────────────────────
    admin_api_key: str = "change-me-admin-key"
    secret_key: str = "change-me-customer-secret"
    access_token_expire_minutes: int = 60 * 24  # 24h
    cookie_secure: bool = False

    # ── Google OAuth ──────────────────────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_return_url: str = "http://localhost:3000"

    # ── Environment & Docs ────────────────────────────────────────────────────
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "EXPLORERS_ENV"),
    )
    docs_enabled: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("DOCS_ENABLED", "ENABLE_DOCS"),
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3100",
        "https://www.explorerschoice.online",
        "https://explorerschoice.online",
    ]
    cors_origin_regex: str | None = (
        r"http://(?:localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):\d{1,5}"
    )

    # ── Local dev escape hatch ────────────────────────────────────────────────
    allow_insecure_defaults: bool = Field(
        default=False,
        validation_alias=AliasChoices("EXPLORERS_ALLOW_INSECURE", "ALLOW_INSECURE_DEFAULTS"),
    )

    # ── Email / SMTP ──────────────────────────────────────────────────────────
    admin_notification_email: str = Field(
        default="infoexplorerschoice@gmail.com",
        validation_alias=AliasChoices("ADMIN_NOTIFICATION_EMAIL", "NOTIFICATION_EMAIL", "SMTP_TO_EMAIL"),
    )
    smtp_host: str = Field(default="", validation_alias=AliasChoices("SMTP_HOST", "MAIL_HOST"))
    smtp_port: int = Field(default=587, validation_alias=AliasChoices("SMTP_PORT", "MAIL_PORT"))
    smtp_username: str = Field(default="", validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER", "MAIL_USERNAME", "MAIL_USER"))
    smtp_password: str = Field(default="", validation_alias=AliasChoices("SMTP_PASSWORD", "SMTP_PASS", "MAIL_PASSWORD", "MAIL_PASS"))
    smtp_from_email: str = Field(default="", validation_alias=AliasChoices("SMTP_FROM_EMAIL", "MAIL_FROM_EMAIL", "MAIL_FROM"))
    smtp_from_name: str = Field(default="Explorers Choice", validation_alias=AliasChoices("SMTP_FROM_NAME", "MAIL_FROM_NAME"))
    smtp_use_tls: bool = Field(default=True, validation_alias=AliasChoices("SMTP_USE_TLS", "SMTP_TLS", "MAIL_TLS"))
    smtp_use_ssl: bool = Field(default=False, validation_alias=AliasChoices("SMTP_USE_SSL", "SMTP_SSL", "MAIL_SSL"))

    # ── Train / Railway API ───────────────────────────────────────────────────
    railway_api_key: str = Field(default="", validation_alias=AliasChoices("RAILWAY_API_KEY", "RAPIDAPI_KEY", "TRAIN_API_KEY"))
    railway_api_host: str = Field(default="irctc1.p.rapidapi.com", validation_alias=AliasChoices("RAILWAY_API_HOST", "RAPIDAPI_HOST"))
    railway_api_url: str = Field(default="https://irctc1.p.rapidapi.com", validation_alias=AliasChoices("RAILWAY_API_URL", "TRAIN_API_BASE_URL"))

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def active_provider(self) -> str:
        return "mysql"

    @property
    def is_mysql(self) -> bool:
        return True

    @model_validator(mode="after")
    def _validate_settings(self) -> "Settings":
        # Validate MySQL connection fields
        if not self.mysql_url.strip():
            for field in ("mysql_host", "mysql_database", "mysql_user", "mysql_password"):
                if not getattr(self, field).strip():
                    raise ValueError(
                        f"{field.upper()} is required. Set it in backend/.env "
                        "(or set MYSQL_URL as a single connection string instead)."
                    )
        mode = (self.mysql_ssl_mode or "").strip().lower()
        if mode not in ("verify-ca", "verify-full", "none"):
            raise ValueError(
                f"MYSQL_SSL_MODE={mode!r} is not valid. Use 'verify-ca', 'verify-full', or 'none'."
            )

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

        if self.docs_enabled is None:
            self.docs_enabled = self.environment.lower() not in ("production", "prod")

        return self


settings = Settings()