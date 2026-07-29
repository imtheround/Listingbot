"""Pydantic models for bot resources."""

from __future__ import annotations

import datetime

from pydantic import BaseModel


class BotCreate(BaseModel):
    """Request body to create a new bot instance."""

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
