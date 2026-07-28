"""Role synchronization background task."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


async def sync_roles() -> None:
    """Synchronize Discord roles based on license status.

    Runs periodically (default every 30 minutes) to assign or remove
    roles from users based on whether they have an active license.
    """
    from autosecure.core.config import settings
    from autosecure.core.database import get_session
    from autosecure.core.state import state
    from autosecure.db.licenses import LicenseRepo

    try:
        client = state.main_bot_client
        if client is None:
            return

        guild_id = settings.discord.guild_id
        member_role_id = settings.discord.member_role
        if not guild_id or not member_role_id:
            return

        guild = client.get_guild(int(guild_id))
        if guild is None:
            return

        member_role = guild.get_role(int(member_role_id))
        if member_role is None:
            return

        async with get_session() as session:
            repo = LicenseRepo(session)
            all_active = await repo.get_all_active()

            users_with_license = {lic.user_id for lic in all_active}

        added = 0
        removed = 0

        for member in guild.members:
            if member.bot:
                continue

            has_license = str(member.id) in users_with_license
            has_role = member_role in member.roles

            if has_license and not has_role:
                try:
                    await member.add_roles(member_role, reason="License active")
                    added += 1
                except Exception as exc:
                    log.debug("Could not add role to %s: %s", member, exc)
            elif not has_license and has_role:
                try:
                    await member.remove_roles(member_role, reason="No active license")
                    removed += 1
                except Exception as exc:
                    log.debug("Could not remove role from %s: %s", member, exc)

        if added or removed:
            log.info("Role sync complete: added=%d removed=%d", added, removed)
    except Exception as exc:
        log.error("Role sync failed: %s", exc)
