"""Dashboard authentication helpers using signed session cookies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from autosecure.core.config import settings
from autosecure.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import Request

log = get_logger("dashboard.auth")


def create_session_token(user_id: str) -> str:
    """Create a signed session cookie value for *user_id*."""
    from itsdangerous import URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.security.session_secret)
    return serializer.dumps(user_id)


def validate_session_token(token: str) -> str | None:
    """Validate a session token and return the user ID, or ``None`` if invalid."""
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.security.session_secret)
    try:
        user_id = serializer.loads(token, max_age=86400 * 7)
        return str(user_id)
    except (BadSignature, SignatureExpired):
        return None


async def get_current_user(request: Request) -> str | None:
    """Extract the current user ID from the session cookie, or ``None``."""
    token = request.cookies.get("session")
    if not token:
        return None
    return validate_session_token(token)
