"""Pydantic models for license resources."""

from __future__ import annotations

from pydantic import BaseModel


class LicenseRedeemRequest(BaseModel):
    """Request body to redeem a license key."""

    license_key: str


class LicenseTransferRequest(BaseModel):
    """Request body to transfer a license."""

    new_user_id: str


class LicenseResponse(BaseModel):
    """Public license representation."""

    license_key: str
    user_id: str
    expires_at: str
    is_active: bool
