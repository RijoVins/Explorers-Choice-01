"""Google OAuth 2.0 sign-in — server-driven flow.

The browser is redirected to Google, authenticates, and lands back on the
backend callback endpoint.  On success the user is found-or-created, an
``ec_session`` session cookie is set, and the browser is redirected to the
configured frontend return URL.

State nonce protection
----------------------
A short-lived in-memory dictionary ``_pending_states`` stores a mapping from
a random token to the frontend ``next`` path the browser requested.  The
token is included as the OAuth ``state`` parameter and verified on callback.
This prevents CSRF-style replay attacks while keeping the design stateless.
"""

import logging
import secrets
import time
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import crud, security
from ..config import settings
from ..database import get_db

router = APIRouter()
logger = logging.getLogger("explorers.oauth")

# ---------------------------------------------------------------------------
# In-memory state nonce store (single-process safe — matches the existing
# in-memory rate-limiter caveat in security.py).
# ---------------------------------------------------------------------------
_pending_states: dict[str, dict] = {}
_STATE_TTL_SECONDS = 600  # 10 minutes


def _generate_state(next_path: str = "/account") -> str:
    token = secrets.token_urlsafe(24)
    _pending_states[token] = {
        "next": next_path,
        "created": time.monotonic(),
    }
    return token


def _consume_state(token: str) -> str | None:
    """Return the ``next`` path if the state is valid, else *None*."""
    info = _pending_states.pop(token, None)
    if info is None:
        return None
    elapsed = time.monotonic() - info["created"]
    if elapsed > _STATE_TTL_SECONDS:
        return None
    next_path = info["next"]
    if not next_path.startswith("/") or next_path.startswith("//"):
        return None
    return next_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _google_enabled() -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def _is_safe_next(next_path: str) -> bool:
    """Validate that a ``next`` path is safe to redirect to (local only)."""
    return bool(next_path) and next_path.startswith("/") and not next_path.startswith("//")


def _build_callback_url() -> str:
    return settings.google_redirect_uri


def _normalize_next(raw: str | None) -> str:
    if raw and _is_safe_next(raw):
        return raw
    return "/account"


# Role-appropriate landing pages. A customer must never be dropped onto /admin
# after signing in, or login would loop forever.
_STAFF_PREFIXES = ("/admin",)
_OWNER_PREFIXES = ("/hotel-owner",)
_CUSTOMER_PREFIXES = ("/account",)


def _safe_post_login_path(raw: str, user) -> str:
    """Return ``raw`` when it is appropriate for this user's role, else the
    default landing page for the role."""
    if not _is_safe_next(raw):
        raw = "/account"
    if user.is_staff:
        return raw if raw.startswith(_STAFF_PREFIXES) else "/admin"
    if user.role == "HOTEL_OWNER":
        return raw if raw.startswith(_OWNER_PREFIXES) else "/hotel-owner"
    # Regular customers may only land on their own area (or anywhere a logged-in
    # visitor is fine, but never /admin or /hotel-owner).
    if raw.startswith(_STAFF_PREFIXES) or raw.startswith(_OWNER_PREFIXES):
        return "/account"
    return raw


# ---------------------------------------------------------------------------
# GET /api/auth/google — redirect the browser to Google's consent screen
# ---------------------------------------------------------------------------
@router.get("/google", status_code=status.HTTP_302_FOUND)
def google_login_init(next: str = "/account"):
    if not _google_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured.",
        )

    next_path = _normalize_next(next)
    state = _generate_state(next_path)

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": _build_callback_url(),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
        "state": state,
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url, status_code=status.HTTP_302_FOUND)


# ---------------------------------------------------------------------------
# GET /api/auth/google/callback — exchange code, set session, redirect home
# ---------------------------------------------------------------------------
@router.get("/google/callback", status_code=status.HTTP_302_FOUND)
def google_login_callback(
    code: str = "",
    state: str = "",
    error: str = "",
    db: Session = Depends(get_db),
):
    if not _google_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured.",
        )

    base_return = settings.google_return_url.rstrip("/")

    # If Google returned an error (user cancelled consent, etc.)
    if error:
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    next_path = _consume_state(state)
    if next_path is None:
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=state_error",
            status_code=status.HTTP_302_FOUND,
        )

    # Exchange authorization code for tokens via Google's token endpoint
    try:
        token_resp = _exchange_code_for_token(code)
        if token_resp is None:
            return RedirectResponse(
                url=f"{base_return}/login?google_auth=error",
                status_code=status.HTTP_302_FOUND,
            )
    except Exception as exc:
        logger.warning("Google token exchange failed: %s", exc)
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    access_token = token_resp.get("access_token")
    if not access_token:
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    # Fetch user profile from Google's userinfo endpoint
    try:
        userinfo = _fetch_userinfo(access_token)
        if userinfo is None or not userinfo.get("email_verified"):
            return RedirectResponse(
                url=f"{base_return}/login?google_auth=email_unverified",
                status_code=status.HTTP_302_FOUND,
            )
    except Exception as exc:
        logger.warning("Google userinfo fetch failed: %s", exc)
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    google_sub = str(userinfo.get("sub", ""))
    email = str(userinfo.get("email", "")).strip().lower()
    full_name = str(userinfo.get("name", "")).strip()

    if not google_sub or not email:
        return RedirectResponse(
            url=f"{base_return}/login?google_auth=error",
            status_code=status.HTTP_302_FOUND,
        )

    # Get a DB session and find-or-create the user
    # 1. Check if user with this Google identity already exists
    user = crud.get_user_by_provider(db, provider="GOOGLE", provider_account_id=google_sub)

    # 2. If no direct provider match, check if email is registered
    if user is None:
        user = crud.get_user(db, email=email)
        if user is not None:
            # If the account was created with a password (EMAIL provider), refuse to auto-link
            # silently to prevent account takeover via Google email matching.
            if user.password_hash and user.auth_provider != "GOOGLE":
                logger.warning(
                    "Refusing auto-link for existing password user %s with Google sub %s",
                    email, google_sub,
                )
                return RedirectResponse(
                    url=f"{base_return}/login?google_auth=account_exists_with_password",
                    status_code=status.HTTP_302_FOUND,
                )
            user = crud.link_google_account(db, user, google_sub)
            logger.info("Linked Google identity to existing account: %s", email)
        else:
            user = crud.create_google_user(
                db,
                email=email,
                full_name=full_name,
                provider_account_id=google_sub,
            )
            logger.info("Created new Google-authenticated user: %s", email)

    # Create session cookie and redirect to frontend
    token = security.create_access_token(user.id, user.token_version or 0)

    redirect_url = f"{base_return}{_safe_post_login_path(next_path, user)}"
    response = RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_302_FOUND,
    )

    response.set_cookie(
        key=security.COOKIE_NAME,
        value=token,
        max_age=security.settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=security.settings.cookie_secure,
        samesite="lax",
        path="/",
    )

    return response


# ---------------------------------------------------------------------------
# Google HTTP helpers (private)
# ---------------------------------------------------------------------------
def _exchange_code_for_token(code: str) -> dict | None:
    """Exchange an authorization code for an access token via googleapis.com."""
    resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": _build_callback_url(),
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if resp.status_code != 200:
        logger.warning(
            "Google token endpoint returned %s: %s",
            resp.status_code,
            resp.text[:200],
        )
        return None
    return resp.json()


def _fetch_userinfo(access_token: str) -> dict | None:
    """Fetch the authenticated user's profile from Google's OIDC userinfo."""
    resp = httpx.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        logger.warning("Google userinfo returned %s", resp.status_code)
        return None
    return resp.json()
