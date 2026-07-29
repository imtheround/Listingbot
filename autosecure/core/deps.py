"""FastAPI dependency injection functions."""

from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from autosecure.core.config import settings
from autosecure.core.database import get_db
from autosecure.core.exceptions import Unauthorized
from autosecure.core.state import state
from autosecure.db.users import UserRepo


async def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> str:
    """Extract and validate user ID from JWT token."""
    if not authorization:
        raise Unauthorized("Missing authorization header")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(
            token,
            settings.security.jwt_secret,
            algorithms=[settings.security.jwt_algorithm],
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise Unauthorized("Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token has expired") from None
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token") from None


async def get_current_user_id_from_cookie(
    session: str | None = Cookie(default=None),
) -> str:
    """Extract user ID from session cookie (for dashboard)."""
    if not session:
        raise Unauthorized("Not authenticated")

    try:
        from itsdangerous import URLSafeTimedSerializer

        serializer = URLSafeTimedSerializer(settings.security.session_secret)
        user_id = serializer.loads(session, max_age=86400 * 7)  # 7 days
        return str(user_id)
    except Exception:
        raise Unauthorized("Invalid session") from None


async def get_optional_user_id(
    authorization: str | None = Header(default=None),
) -> str | None:
    """Extract user ID if authorization is provided, else None."""
    if not authorization:
        return None
    try:
        return await get_current_user_id(authorization)
    except Unauthorized:
        return None


async def require_owner(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: AsyncSession = Depends(get_db),
) -> str:
    """Require the user to be an owner (config list or DB role='owner')."""
    if state.is_owner(user_id):
        return user_id
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user and user.permissions.get("role") == "owner":
        return user_id
    raise HTTPException(status_code=403, detail="Owner access required")


async def require_active_license(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: AsyncSession = Depends(get_db),
) -> str:
    """Require the user to have an active (non-expired) license."""
    user_repo = UserRepo(db)
    has_license = await user_repo.has_active_license(user_id)
    if not has_license and not state.is_owner(user_id):
        raise HTTPException(status_code=403, detail="Active license required")
    return user_id


# Type aliases for FastAPI dependencies
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[str, Depends(get_current_user_id)]
OptionalUser = Annotated[str | None, Depends(get_optional_user_id)]
OwnerUser = Annotated[str, Depends(require_owner)]
LicensedUser = Annotated[str, Depends(require_active_license)]
