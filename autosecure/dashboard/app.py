"""Dashboard routes serving Jinja2 templates with HTMX."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from autosecure.dashboard.auth import create_session_token, get_current_user

templates = Jinja2Templates(directory="autosecure/dashboard/templates")
router = APIRouter(tags=["dashboard"])


async def _require_auth(request: Request) -> str | None:
    """Return user ID if authenticated, else None."""
    return await get_current_user(request)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_overview(request: Request) -> Response:
    """Main dashboard overview page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user_id": user_id, "page": "overview"},
    )


@router.get("/dashboard/accounts", response_class=HTMLResponse)
async def dashboard_accounts(request: Request) -> Response:
    """Accounts list page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "accounts.html",
        {"request": request, "user_id": user_id, "page": "accounts"},
    )


@router.get("/dashboard/bots", response_class=HTMLResponse)
async def dashboard_bots(request: Request) -> Response:
    """Bot management page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "bots.html",
        {"request": request, "user_id": user_id, "page": "bots"},
    )


@router.get("/dashboard/licenses", response_class=HTMLResponse)
async def dashboard_licenses(request: Request) -> Response:
    """License management page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "licenses.html",
        {"request": request, "user_id": user_id, "page": "licenses"},
    )


@router.get("/dashboard/emails", response_class=HTMLResponse)
async def dashboard_emails(request: Request) -> Response:
    """Email inbox page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "emails.html",
        {"request": request, "user_id": user_id, "page": "emails"},
    )


@router.get("/dashboard/settings", response_class=HTMLResponse)
async def dashboard_settings(request: Request) -> Response:
    """User settings page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "user_id": user_id, "page": "settings"},
    )


@router.get("/dashboard/logs", response_class=HTMLResponse)
async def dashboard_logs(request: Request) -> Response:
    """Activity logs page."""
    user_id = await _require_auth(request)
    if not user_id:
        return RedirectResponse(url="/dashboard/login", status_code=302)

    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "user_id": user_id, "page": "logs"},
    )


@router.post("/dashboard/login")
async def dashboard_login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
) -> Response:
    """Process dashboard login form submission."""
    from passlib.hash import bcrypt
    from sqlalchemy import select

    from autosecure.core.database import get_session
    from autosecure.models.user import User

    async with get_session() as session:
        stmt = select(User).where(User.user_id == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if user is None or not bcrypt.verify(password, user.permissions.get("password_hash", "")):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401,
        )

    token = create_session_token(user.user_id)
    redirect = RedirectResponse(url="/dashboard", status_code=302)
    redirect.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400 * 7,
    )
    return redirect


@router.get("/dashboard/logout")
async def dashboard_logout(request: Request) -> Response:
    """Clear session cookie and redirect to login."""
    redirect = RedirectResponse(url="/dashboard/login", status_code=302)
    redirect.delete_cookie(key="session")
    return redirect
