"""Account management routes."""

from __future__ import annotations

import math
from fastapi import APIRouter, HTTPException, Query

from autosecure.api.models.accounts import AccountCreate, AccountListResponse, AccountResponse
from autosecure.core.deps import CurrentUser, DBSession
from autosecure.db.accounts import AccountRepo
from autosecure.services.hypixel import get_player_stats

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=AccountListResponse)
async def list_accounts(
    user_id: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: str | None = Query(None),
) -> AccountListResponse:
    """List accounts for the authenticated user with pagination and search."""
    repo = AccountRepo(db)
    offset = (page - 1) * per_page

    if search:
        accounts = await repo.search(search, limit=per_page)
    else:
        accounts = await repo.get_by_user(user_id, limit=per_page, offset=offset)

    total = await repo.count_by_user(user_id)
    pages = math.ceil(total / per_page) if total else 0

    return AccountListResponse(
        accounts=[
            AccountResponse(
                uid=a.uid,
                username=a.username,
                email=a.email,
                networth=a.stats.get("networth") if a.stats else None,
                created_at=a.created_at,
            )
            for a in accounts
        ],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{uid}", response_model=AccountResponse)
async def get_account(uid: str, user_id: CurrentUser, db: DBSession) -> AccountResponse:
    """Get a single account by UID."""
    repo = AccountRepo(db)
    data = await repo.get_account_with_user(uid)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")

    account = data["account"]
    mapping = data["mapping"]
    if mapping.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return AccountResponse(
        uid=account.uid,
        username=account.username,
        email=account.email,
        networth=account.stats.get("networth") if account.stats else None,
        created_at=account.created_at,
    )


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    body: AccountCreate,
    user_id: CurrentUser,
    db: DBSession,
) -> AccountResponse:
    """Register a new account."""
    repo = AccountRepo(db)
    account = await repo.insert(
        {
            "uid": body.uid,
            "user_id": user_id,
            "username": body.username,
            "email": body.email,
            "recovery_code": body.recovery_code,
        }
    )
    return AccountResponse(
        uid=account.uid,
        username=account.username,
        email=account.email,
        created_at=account.created_at,
    )


@router.delete("/{uid}")
async def delete_account(uid: str, user_id: CurrentUser, db: DBSession) -> dict[str, str]:
    """Delete an account by UID."""
    repo = AccountRepo(db)
    data = await repo.get_account_with_user(uid)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if data["mapping"].user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    deleted = await repo.delete_by_uid(uid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"success": True, "message": "Account deleted"}


@router.get("/{uid}/stats")
async def get_account_stats(uid: str, user_id: CurrentUser, db: DBSession) -> dict:
    """Fetch Hypixel stats for an account."""
    repo = AccountRepo(db)
    data = await repo.get_account_with_user(uid)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if data["mapping"].user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    stats = await get_player_stats(data["account"].username)
    return {"uid": uid, "stats": stats}
