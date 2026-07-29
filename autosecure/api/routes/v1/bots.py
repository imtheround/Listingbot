"""Bot management routes."""

from __future__ import annotations

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException

from autosecure.api.models.bots import BotCreate, BotResponse, BotRestartResponse
from autosecure.core.deps import CurrentUser, DBSession
from autosecure.core.state import state
from autosecure.db.bots import BotRepo
from autosecure.models.bot import AutoSecure

router = APIRouter(prefix="/bots", tags=["bots"])


def _bot_response(bot: AutoSecure) -> BotResponse:
    key = state.get_bot_key(bot.user_id, bot.botnumber)
    status = "running" if key in state.active_bots else "stopped"
    return BotResponse(
        id=bot.id,
        user_id=bot.user_id,
        botnumber=bot.botnumber,
        status=status,
        created_at=bot.created_at,
    )


@router.get("", response_model=list[BotResponse])
async def list_bots(user_id: CurrentUser, db: DBSession) -> list[BotResponse]:
    """List all bot instances for the authenticated user."""
    repo = BotRepo(db)
    bots = await repo.get_by_user(user_id)
    return [_bot_response(b) for b in bots]


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotResponse:
    """Get bot details by ID."""
    repo = BotRepo(db)
    bot = await repo.get(AutoSecure, bot_id)
    if bot is None or bot.user_id != user_id:
        raise HTTPException(status_code=404, detail="Bot not found")
    return _bot_response(bot)


@router.post("", response_model=BotResponse, status_code=201)
async def create_bot(body: BotCreate, user_id: CurrentUser, db: DBSession) -> BotResponse:
    """Create a new bot instance."""
    repo = BotRepo(db)
    existing = await repo.get_by_user(user_id)
    botnumber = max((b.botnumber for b in existing), default=0) + 1

    bot = await repo.create(
        {
            "user_id": user_id,
            "botnumber": botnumber,
            "token": body.token,
            "domain": "autosecure.dev",
            "verified": False,
        }
    )
    return _bot_response(bot)


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    user_id: CurrentUser,
    db: DBSession,
    domain: str | None = None,
    activity: dict | None = None,
    dmmode: bool | None = None,
) -> BotResponse:
    """Update bot configuration."""
    repo = BotRepo(db)
    bot = await repo.get(AutoSecure, bot_id)
    if bot is None or bot.user_id != user_id:
        raise HTTPException(status_code=404, detail="Bot not found")

    updates: dict = {}
    if domain is not None:
        updates["domain"] = domain
    if activity is not None:
        updates["activity"] = activity
    if dmmode is not None:
        updates["dmmode"] = dmmode

    if updates:
        await repo.update(bot, **updates)

    return _bot_response(bot)


@router.delete("/{bot_id}")
async def delete_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> dict[str, str]:
    """Destroy a bot instance."""
    repo = BotRepo(db)
    bot = await repo.get(AutoSecure, bot_id)
    if bot is None or bot.user_id != user_id:
        raise HTTPException(status_code=404, detail="Bot not found")

    state.remove_bot(bot.user_id, bot.botnumber)
    await repo.delete(bot.user_id, bot.botnumber)
    return {"success": True, "message": "Bot destroyed"}


@router.post("/{bot_id}/restart", response_model=BotRestartResponse)
async def restart_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotRestartResponse:
    """Restart a bot instance."""
    repo = BotRepo(db)
    bot = await repo.get(AutoSecure, bot_id)
    if bot is None or bot.user_id != user_id:
        raise HTTPException(status_code=404, detail="Bot not found")

    state.remove_bot(bot.user_id, bot.botnumber)
    return BotRestartResponse(success=True, message="Bot restart queued")
