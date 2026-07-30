"""Bot management routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from autosecure.api.models.bots import BotCreate, BotResponse, BotRestartResponse
from autosecure.core.deps import CurrentUser, DBSession
from autosecure.core.state import state
from autosecure.db.bots import BotRepo
from autosecure.models.bot import AutoSecure

router = APIRouter(prefix="/bots", tags=["bots"])


class BotUpdateRequest(BaseModel):
    """Request body to update bot configuration."""

    domain: str | None = None
    activity: dict | None = None
    dmmode: bool | None = None


class BotDetailResponse(BotResponse):
    """Bot representation with config details."""

    domain: str = "autosecure.dev"
    verified: bool = False
    dmmode: bool = False
    activity: dict | None = None


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


def _bot_detail_response(bot: AutoSecure) -> BotDetailResponse:
    key = state.get_bot_key(bot.user_id, bot.botnumber)
    status = "running" if key in state.active_bots else "stopped"
    return BotDetailResponse(
        id=bot.id,
        user_id=bot.user_id,
        botnumber=bot.botnumber,
        status=status,
        created_at=bot.created_at,
        domain=bot.domain,
        verified=bot.verified,
        dmmode=bot.dmmode,
        activity=bot.activity,
    )


async def _get_owned_bot(bot_id: int, user_id: str, db) -> AutoSecure:
    """Fetch a bot by ID and verify ownership."""
    repo = BotRepo(db)
    bot = await repo.get(AutoSecure, bot_id)
    if bot is None or bot.user_id != user_id:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@router.get("", response_model=list[BotResponse])
async def list_bots(user_id: CurrentUser, db: DBSession) -> list[BotResponse]:
    """List all bot instances for the authenticated user."""
    repo = BotRepo(db)
    bots = await repo.get_by_user(user_id)
    return [_bot_response(b) for b in bots]


@router.get("/{bot_id}", response_model=BotDetailResponse)
async def get_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotDetailResponse:
    """Get bot details by ID, including configuration."""
    bot = await _get_owned_bot(bot_id, user_id, db)
    return _bot_detail_response(bot)


@router.post("", response_model=BotResponse, status_code=201)
async def create_bot(body: BotCreate, user_id: CurrentUser, db: DBSession) -> BotResponse:
    """Create a new bot instance."""
    if not body.token or body.token.strip() == "":
        raise HTTPException(status_code=422, detail="Token is required")

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


@router.put("/{bot_id}", response_model=BotDetailResponse)
async def update_bot(
    bot_id: int,
    body: BotUpdateRequest,
    user_id: CurrentUser,
    db: DBSession,
) -> BotDetailResponse:
    """Update bot configuration (domain, activity, dmmode)."""
    bot = await _get_owned_bot(bot_id, user_id, db)
    repo = BotRepo(db)

    updates: dict = {}
    if body.domain is not None:
        updates["domain"] = body.domain
    if body.activity is not None:
        updates["activity"] = body.activity
    if body.dmmode is not None:
        updates["dmmode"] = body.dmmode

    if updates:
        await repo.update(bot, **updates)

    return _bot_detail_response(bot)


@router.delete("/{bot_id}")
async def delete_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> dict[str, str]:
    """Destroy a bot instance. Stops it if running."""
    bot = await _get_owned_bot(bot_id, user_id, db)
    repo = BotRepo(db)

    # Stop the bot if it's running
    client = state.remove_bot(bot.user_id, bot.botnumber)
    if client is not None and hasattr(client, "close"):
        try:
            await client.close()
        except Exception:
            pass

    await repo.delete(bot.user_id, bot.botnumber)
    return {"success": True, "message": "Bot destroyed"}


@router.post("/{bot_id}/start", response_model=BotRestartResponse)
async def start_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotRestartResponse:
    """Start a stopped bot instance."""
    bot = await _get_owned_bot(bot_id, user_id, db)

    key = state.get_bot_key(bot.user_id, bot.botnumber)
    if key in state.active_bots:
        return BotRestartResponse(success=True, message="Bot is already running")

    # Create and start the worker bot
    try:
        raise HTTPException(status_code=501, detail="Bot start not yet implemented for web platform")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {e}") from e

    return BotRestartResponse(success=True, message="Bot started")


@router.post("/{bot_id}/stop", response_model=BotRestartResponse)
async def stop_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotRestartResponse:
    """Stop a running bot instance."""
    bot = await _get_owned_bot(bot_id, user_id, db)

    key = state.get_bot_key(bot.user_id, bot.botnumber)
    if key not in state.active_bots:
        return BotRestartResponse(success=True, message="Bot is already stopped")

    client = state.remove_bot(bot.user_id, bot.botnumber)
    if client is not None and hasattr(client, "close"):
        try:
            await client.close()
        except Exception:
            pass

    return BotRestartResponse(success=True, message="Bot stopped")


@router.post("/{bot_id}/restart", response_model=BotRestartResponse)
async def restart_bot(bot_id: int, user_id: CurrentUser, db: DBSession) -> BotRestartResponse:
    """Restart a bot instance (stop then start)."""
    bot = await _get_owned_bot(bot_id, user_id, db)

    # Stop if running
    client = state.remove_bot(bot.user_id, bot.botnumber)
    if client is not None and hasattr(client, "close"):
        try:
            await client.close()
        except Exception:
            pass

    # Start fresh
    try:
        raise HTTPException(status_code=501, detail="Bot restart not yet implemented for web platform")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart bot: {e}") from e

    return BotRestartResponse(success=True, message="Bot restarted")
