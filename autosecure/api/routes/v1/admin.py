"""Admin-only routes for user and license management."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from autosecure.core.deps import DBSession, OwnerUser
from autosecure.core.database import get_db
from autosecure.db.users import UserRepo
from autosecure.models.audit import AuditLog
from autosecure.models.blacklist import Blacklisted
from autosecure.models.license import License, UsedLicense
from autosecure.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminUserResponse(BaseModel):
    user_id: str
    permissions: dict
    claiming: str
    rest_split: int


class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int


class BlacklistUpdate(BaseModel):
    client_id: str
    reason: str = ""


class LicenseGenerateRequest(BaseModel):
    count: int = 1
    expiry: str = "30d"


class LicenseGenerateResponse(BaseModel):
    licenses: list[str]
    count: int


class AdminLicenseResponse(BaseModel):
    license_key: str
    user_id: str | None = None
    expires_at: str
    is_used: bool


class AdminLicenseListResponse(BaseModel):
    licenses: list[AdminLicenseResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: int
    timestamp: str
    actor_id: str
    action: str
    target_type: str | None = None
    target_id: str | None = None
    details: dict | None = None
    success: bool
    ip_address: str | None = None


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
    page: int
    pages: int


@router.get("/users", response_model=AdminUserListResponse)
async def list_all_users(
    owner: OwnerUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> AdminUserListResponse:
    """List all users (owner only)."""
    repo = UserRepo(db)
    users = await repo.list(User, limit=per_page, offset=(page - 1) * per_page)
    total = await repo.count(User)

    return AdminUserListResponse(
        users=[
            AdminUserResponse(
                user_id=u.user_id,
                permissions=u.permissions,
                claiming=u.claiming,
                rest_split=u.rest_split,
            )
            for u in users
        ],
        total=total,
    )


@router.delete("/users/{user_id}")
async def force_delete_user(
    user_id: str,
    owner: OwnerUser,
    db: DBSession,
) -> dict[str, str]:
    """Force-delete a user (owner only)."""
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.delete(user)
    return {"success": True, "message": f"User {user_id} deleted"}


@router.put("/blacklist")
async def update_blacklist(
    body: BlacklistUpdate,
    owner: OwnerUser,
    db: DBSession,
) -> dict[str, str]:
    """Add or update a blacklist entry (owner only)."""
    entry = Blacklisted(client_id=body.client_id, reason=body.reason)
    db.add(entry)
    await db.flush()
    return {"success": True, "message": f"{body.client_id} blacklisted"}


@router.get("/licenses", response_model=AdminLicenseListResponse)
async def list_all_licenses(
    owner: OwnerUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> AdminLicenseListResponse:
    """List all licenses (owner only)."""
    offset = (page - 1) * per_page

    stmt = select(License).limit(per_page).offset(offset)
    result = await db.execute(stmt)
    raw_licenses = list(result.scalars().all())

    used_stmt = select(UsedLicense)
    used_result = await db.execute(used_stmt)
    used_map = {u.license: u.user_id for u in used_result.scalars().all()}

    count_stmt = select(__import__("sqlalchemy").func.count()).select_from(License)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return AdminLicenseListResponse(
        licenses=[
            AdminLicenseResponse(
                license_key=lic.license,
                user_id=used_map.get(lic.license),
                expires_at=lic.expiry,
                is_used=lic.license in used_map,
            )
            for lic in raw_licenses
        ],
        total=total,
    )


@router.post("/licenses/generate", response_model=LicenseGenerateResponse, status_code=201)
async def generate_licenses(
    body: LicenseGenerateRequest,
    owner: OwnerUser,
    db: DBSession,
) -> LicenseGenerateResponse:
    """Generate new license keys (owner only)."""
    keys: list[str] = []
    for _ in range(body.count):
        key = f"ASC-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
        license_ = License(license=key, expiry=body.expiry)
        db.add(license_)
        keys.append(key)

    await db.flush()
    return LicenseGenerateResponse(licenses=keys, count=body.count)


@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    owner: OwnerUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    action: str | None = None,
    actor_id: str | None = None,
    target_type: str | None = None,
    success: bool | None = None,
) -> AuditLogListResponse:
    """List audit logs with optional filters (owner only)."""
    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)

    if action:
        stmt = stmt.where(AuditLog.action == action)
        count_stmt = count_stmt.where(AuditLog.action == action)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
        count_stmt = count_stmt.where(AuditLog.actor_id == actor_id)
    if target_type:
        stmt = stmt.where(AuditLog.target_type == target_type)
        count_stmt = count_stmt.where(AuditLog.target_type == target_type)
    if success is not None:
        stmt = stmt.where(AuditLog.success == success)
        count_stmt = count_stmt.where(AuditLog.success == success)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    offset = (page - 1) * per_page
    stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(per_page).offset(offset)
    result = await db.execute(stmt)
    logs = list(result.scalars().all())

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                timestamp=log.timestamp.isoformat() if log.timestamp else "",
                 actor_id=log.actor_id,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                details=log.details,
                success=log.success,
                ip_address=log.actor_ip,
            )
            for log in logs
        ],
        total=total,
        page=page,
        pages=max(1, -(-total // per_page)),
    )


# ── Security Endpoints ────────────────────────────────────────────────


class BlockedIPResponse(BaseModel):
    ip: str
    blocked_until: float
    remaining_seconds: int


class BlockedIPListResponse(BaseModel):
    blocked_ips: list[BlockedIPResponse]
    total: int


class SuspiciousEventResponse(BaseModel):
    event_type: str
    ip: str
    user_agent: str
    user_id: str | None
    details: dict
    timestamp: float


class SuspiciousEventListResponse(BaseModel):
    events: list[SuspiciousEventResponse]
    total: int


class UnblockRequest(BaseModel):
    ip: str


@router.get("/security/blocked", response_model=BlockedIPListResponse)
async def list_blocked_ips(
    owner: OwnerUser,
) -> BlockedIPListResponse:
    """List all currently blocked IPs (owner only)."""
    from autosecure.core.security_middleware import anti_abuse

    blocked = anti_abuse.get_blocked_ips()
    return BlockedIPListResponse(
        blocked_ips=[
            BlockedIPResponse(
                ip=b["ip"],
                blocked_until=b["blocked_until"],
                remaining_seconds=b["remaining_seconds"],
            )
            for b in blocked
        ],
        total=len(blocked),
    )


@router.post("/security/unblock")
async def unblock_ip(
    body: UnblockRequest,
    owner: OwnerUser,
) -> dict[str, str]:
    """Manually unblock an IP address (owner only)."""
    from autosecure.core.security_middleware import anti_abuse

    success = anti_abuse.unblock_ip(body.ip)
    if not success:
        raise HTTPException(status_code=404, detail="IP not found in block list")
    return {"success": True, "message": f"IP {body.ip} unblocked"}


@router.get("/security/suspicious", response_model=SuspiciousEventListResponse)
async def list_suspicious_events(
    owner: OwnerUser,
    limit: int = Query(50, ge=1, le=200),
) -> SuspiciousEventListResponse:
    """List recent suspicious events (owner only)."""
    from autosecure.core.security_middleware import anti_abuse

    events = anti_abuse.get_events(limit=limit)
    return SuspiciousEventListResponse(
        events=[
            SuspiciousEventResponse(
                event_type=e["event_type"],
                ip=e["ip"],
                user_agent=e["user_agent"],
                user_id=e["user_id"],
                details=e["details"],
                timestamp=e["timestamp"],
            )
            for e in events
        ],
        total=len(events),
    )
