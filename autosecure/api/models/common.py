"""Shared Pydantic models for error, success, and health responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured error payload."""

    error: str
    detail: str = ""


class SuccessResponse(BaseModel):
    """Confirmation payload."""

    success: bool = True
    message: str = ""


class HealthResponse(BaseModel):
    """Health check result."""

    status: str = "ok"
    checks: dict[str, bool] = Field(default_factory=dict)
    uptime: float = 0.0
