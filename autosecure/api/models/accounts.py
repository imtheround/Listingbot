"""Pydantic models for account resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    import datetime


class AccountCreate(BaseModel):
    """Request body to register a new account."""

    uid: str
    username: str
    email: str | None = None
    recovery_code: str | None = None
    method: str = "microsoft"


class AccountResponse(BaseModel):
    """Public account representation."""

    uid: str
    username: str
    email: str | None = None
    method: str = "microsoft"
    networth: int | None = None
    created_at: datetime.datetime | None = None


class AccountListResponse(BaseModel):
    """Paginated list of accounts."""

    accounts: list[AccountResponse]
    total: int
    page: int
    pages: int
