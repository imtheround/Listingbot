"""Authentication routes for JWT token management + Google OAuth."""

from __future__ import annotations

import secrets
import time
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from autosecure.api.models.auth import LoginResponse, RefreshRequest, LoginRequest
from autosecure.core.config import settings
from autosecure.core.database import get_db
from autosecure.core.exceptions import Unauthorized
from autosecure.core.logging import get_logger
from autosecure.core.redis import get_redis
from autosecure.db.users import UserRepo

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = get_logger("api.auth")
router = APIRouter(prefix="/auth", tags=["auth"])


def _create_access_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "type": "access",
        "exp": int(time.time()) + settings.security.jwt_access_expiry,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, settings.security.jwt_secret, algorithm=settings.security.jwt_algorithm)


def _create_refresh_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": int(time.time()) + settings.security.jwt_refresh_expiry,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, settings.security.jwt_secret, algorithm=settings.security.jwt_algorithm)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.security.jwt_secret, algorithms=[settings.security.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token has expired") from None
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token") from None


def _issue_tokens(user_id: str) -> dict:
    """Create access + refresh tokens and return as dict."""
    access_token = _create_access_token(user_id)
    refresh_token = _create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.security.jwt_access_expiry,
    }


# ── Google OAuth ──────────────────────────────────────────────────────


@router.get("/google")
async def google_login(captcha: str = Query(default="")):
    """Redirect to Google OAuth consent screen. Requires hCaptcha."""
    # Verify hCaptcha
    if settings.hcaptcha.enabled:
        from autosecure.services.hcaptcha import verify_hcaptcha

        result = await verify_hcaptcha(captcha)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Captcha verification failed")

    state = secrets.token_urlsafe(32)
    r = get_redis()
    await r.set(f"oauth_state:{state}", "1", ex=settings.oauth.state_expiry_seconds)

    params = {
        "client_id": settings.oauth.google_client_id,
        "redirect_uri": settings.oauth.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "select_account",
    }
    url = f"{settings.oauth.google_auth_url}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback: exchange code, create/find user, issue JWT."""
    # 1. Verify state
    r = get_redis()
    stored = await r.get(f"oauth_state:{state}")
    if not stored:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    await r.delete(f"oauth_state:{state}")

    # 2. Exchange code for tokens
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            settings.oauth.google_token_url,
            data={
                "code": code,
                "client_id": settings.oauth.google_client_id,
                "client_secret": settings.oauth.google_client_secret,
                "redirect_uri": settings.oauth.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain Google access token")

    # 3. Fetch user info from Google
    async with httpx.AsyncClient(timeout=10) as client:
        userinfo_resp = await client.get(
            settings.oauth.google_userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo_resp.raise_for_status()
        google_user = userinfo_resp.json()

    google_id = google_user.get("sub")
    email = google_user.get("email", "")
    name = google_user.get("name", "")
    avatar_url = google_user.get("picture", "")

    if not google_id:
        raise HTTPException(status_code=400, detail="Google ID not found in response")

    # 4. Find or create user
    repo = UserRepo(db)
    user = await repo.get_by_google_id(google_id)

    if user is None:
        # First time — create user with 'user' role
        user_id = f"google_{google_id}"
        user = await repo.create_from_google(
            user_id=user_id,
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
        )
        log.info("user_created_via_oauth", user_id=user_id, email=email)

    # 5. Check if banned
    if user.is_banned or user.role == "banned":
        raise HTTPException(status_code=403, detail="Account is banned")

    # 6. Update profile fields (Google data may change)
    if user.name != name:
        user.name = name
    if user.avatar_url != avatar_url:
        user.avatar_url = avatar_url
    if user.email != email:
        user.email = email
    await db.flush()

    # 7. Log login
    await repo.record_login(user.user_id)

    # 8. Issue JWT tokens
    tokens = _issue_tokens(user.user_id)

    log.info("user_logged_in_google", user_id=user.user_id, email=email)

    # 9. Redirect to frontend callback with tokens as query params
    callback_url = f"/auth/google/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    return RedirectResponse(url=callback_url)


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Email + password login. Returns JWT tokens."""
    repo = UserRepo(db)
    user = await repo.get_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password hash in permissions dict
    from passlib.hash import bcrypt
    stored_hash = user.permissions.get("password_hash", "")
    if not stored_hash or not bcrypt.verify(body.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if banned
    if user.is_banned or user.role == "banned":
        raise HTTPException(status_code=403, detail="Account is banned")

    # Record login
    await repo.record_login(user.user_id)

    tokens = _issue_tokens(user.user_id)
    return LoginResponse(**tokens)


# ── Token Management ──────────────────────────────────────────────────


@router.get("/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    """Return current user info from JWT."""
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise Unauthorized("Missing authorization header")

    payload = _decode_token(auth[7:])
    user_id = payload.get("user_id")
    if not user_id:
        raise Unauthorized("Invalid token")

    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user is None:
        raise Unauthorized("User not found")

    if user.is_banned or user.role == "banned":
        raise HTTPException(status_code=403, detail="Account is banned")

    return {
        "user_id": user.user_id,
        "google_id": user.google_id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "is_banned": user.is_banned,
        "email_verified": user.email_verified,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "login_count": user.login_count,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/refresh", response_model=LoginResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Exchange a refresh token for new access + refresh tokens."""
    payload = _decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise Unauthorized("Invalid token type")

    user_id = payload["user_id"]
    r = get_redis()
    await r.set(f"revoked:{body.refresh_token}", "1", ex=settings.security.jwt_refresh_expiry)

    # Check user is not banned
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user and (user.is_banned or user.role == "banned"):
        raise HTTPException(status_code=403, detail="Account is banned")

    tokens = _issue_tokens(user_id)
    return LoginResponse(**tokens)


@router.post("/logout")
async def logout(
    authorization: str | None = None,
) -> dict[str, str]:
    """Invalidate the current access token."""
    if not authorization:
        raise Unauthorized("Missing authorization header")

    token = authorization.replace("Bearer ", "")
    payload = _decode_token(token)
    r = get_redis()
    exp = payload.get("exp", int(time.time()) + 3600)
    ttl = max(1, exp - int(time.time()))
    await r.set(f"revoked:{token}", "1", ex=ttl)

    log.info("user_logged_out", user_id=payload.get("user_id"))
    return {"success": True, "message": "Logged out"}
