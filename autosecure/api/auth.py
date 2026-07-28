"""Authentication routes for JWT token management."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import jwt
from fastapi import APIRouter, Depends
from passlib.hash import bcrypt
from sqlalchemy import select

from autosecure.api.models.auth import LoginRequest, LoginResponse, RefreshRequest
from autosecure.core.config import settings
from autosecure.core.database import get_db
from autosecure.core.exceptions import InvalidCredentials, Unauthorized
from autosecure.core.logging import get_logger
from autosecure.core.redis import get_redis
from autosecure.models.user import User

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


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Authenticate with email and password, returning JWT tokens."""
    stmt = select(User).where(User.user_id == body.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not bcrypt.verify(body.password, user.permissions.get("password_hash", "")):
        raise InvalidCredentials()

    access_token = _create_access_token(user.user_id)
    refresh_token = _create_refresh_token(user.user_id)

    log.info("user_logged_in", user_id=user.user_id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.security.jwt_access_expiry,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Exchange a refresh token for new access + refresh tokens."""
    payload = _decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise Unauthorized("Invalid token type")

    user_id = payload["user_id"]
    r = get_redis()
    await r.set(f"revoked:{body.refresh_token}", "1", ex=settings.security.jwt_refresh_expiry)

    access_token = _create_access_token(user_id)
    refresh_token = _create_refresh_token(user_id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.security.jwt_access_expiry,
    )


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
