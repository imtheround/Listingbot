"""Ban checking and enforcement service."""

from __future__ import annotations

from typing import Any

from autosecure.core.logging import get_logger
from autosecure.services.minecraft.bancheck import BanResult, check_ban

log = get_logger("services.banning")


async def check_account_ban(
    ssid: str,
    proxy: str | None = None,
) -> BanResult:
    """Check if a Minecraft account is banned on Hypixel.

    Args:
        ssid: Minecraft Session ID (access token).
        proxy: Optional proxy URL for the connection.

    Returns:
        BanResult with ban status and details.
    """
    log.info("banning.check_account", has_proxy=proxy is not None)
    return await check_ban(ssid, proxy)


async def enforce_ban(
    account_data: dict[str, Any],
    action: str,
    db: Any,
) -> None:
    """Enforce a ban action on an account.

    Args:
        account_data: Account data with ssid, username, etc.
        action: One of "quarantine", "blacklist", "notify".
        db: Database session.
    """
    username = account_data.get("username", "Unknown")
    account_data.get("ssid", "")
    account_data.get("user_id", "")

    log.info("banning.enforce", username=username, action=action)

    if action == "quarantine":
        await _quarantine_account(account_data, db)
    elif action == "blacklist":
        await _blacklist_account(account_data, db)
    elif action == "notify":
        await _notify_ban(account_data, db)
    else:
        log.warning("banning.enforce.unknown_action", action=action)


async def _quarantine_account(account_data: dict[str, Any], db: Any) -> None:
    """Quarantine a banned account.

    Args:
        account_data: Account data dictionary.
        db: Database session.
    """
    try:
        from autosecure.services.quarantine import add_quarantine

        await add_quarantine(
            username=account_data.get("username", "Unknown"),
            ssid=account_data.get("ssid", ""),
            uuid=account_data.get("uuid", ""),
            user_id=account_data.get("user_id", ""),
            reason="Auto-quarantined due to ban",
            db=db,
        )
        log.info("banning.quarantined", username=account_data.get("username"))
    except Exception as e:
        log.error("banning.quarantine_failed", error=str(e))


async def _blacklist_account(account_data: dict[str, Any], db: Any) -> None:
    """Blacklist a banned account.

    Args:
        account_data: Account data dictionary.
        db: Database session.
    """
    try:
        from autosecure.db.blacklist import BlacklistRepo

        repo = BlacklistRepo(db)
        email = account_data.get("email", "")
        if email:
            await repo.add_email(email, "Auto-blacklisted due to ban")
            log.info("banning.blacklisted_email", email=email)
    except Exception as e:
        log.error("banning.blacklist_failed", error=str(e))


async def _notify_ban(account_data: dict[str, Any], db: Any) -> None:
    """Send a ban notification to the user.

    Args:
        account_data: Account data dictionary.
        db: Database session.
    """
    try:
        from autosecure.services.notifications import send_notification

        user_id = account_data.get("user_id", "")
        username = account_data.get("username", "Unknown")

        if user_id:
            await send_notification(
                user_id=user_id,
                title="Account Banned",
                description=f"**{username}** has been banned on Hypixel.",
                db=db,
            )
            log.info("banning.notified", username=username, user_id=user_id)
    except Exception as e:
        log.error("banning.notify_failed", error=str(e))
