"""Pydantic models for bot resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    import datetime


class BotCreate(BaseModel):
    """Request body to create a new bot instance."""

    user_id: str
    token: str


class BotResponse(BaseModel):
    """Public bot representation."""

    id: int
    user_id: str
    botnumber: int
    status: str = "stopped"
    created_at: datetime.datetime | None = None


class BotRestartResponse(BaseModel):
    """Result of a bot restart operation."""

    success: bool
    message: str
