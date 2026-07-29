# AutoSecure — Development Plan

> Complete guide to ship a production-ready AutoSecure. Covers backend API, Next.js dashboard, Discord bot, and deployment.

## Current Status (2026-07-29)

### Legend
| Symbol | Meaning |
|--------|---------|
| ✅ | Done |
| 🔧 | Needs work / partially done |
| ❌ | Not started |
| 🚫 | Blocked |

### Status Summary

| Layer | Status | Notes |
|---|---|---|
| **Backend API** | | |
| 33 route endpoints | ✅ | All defined, registered in router |
| JWT auth (login/refresh/logout) | ✅ | Works, tokens returned on POST /auth/login |
| Health check | ✅ | /health returns DB + Redis status |
| Account CRUD | ✅ | List, get, create, delete — ownership-scoped |
| Bot CRUD | ✅ | List, get, create, update, delete |
| License redeem/transfer/status | ✅ | User endpoints work |
| Admin endpoints (users, licenses) | ✅ | Owner-only |
| Email inbox + watch | ✅ | Register + fetch emails |
| Webhook subscriptions | ✅ | CRUD with ownership check |
| User profile + settings | ✅ | View own profile, update settings |
| SSE events endpoint | ❌ | No real-time push |
| Status summary page | ❌ | No aggregated stats endpoint |
| **Frontend Dashboard** | | |
| Login page | ✅ | JWT + cookie, no sidebar |
| Overview page | 🔧 | 4 stat cards + health card, but shapes often mismatch API response |
| Accounts list | 🔧 | Table renders, search works — no add/delete UI |
| Account detail | 🔧 | Renders details card + licenses card — field names mismatch API |
| Bots list | 🔧 | Table + create/delete — create sends placeholder token |
| Bot detail | ❌ | No bot detail/edit page |
| Bot start/stop/restart | ❌ | No action buttons |
| Licenses list | 🔧 | Read-only table — no generate/redeem/transfer |
| Email inbox | 🔧 | Watch + fetch work — no unwatch, no detail view |
| Settings | ❌ | Empty input box — no actual settings editing |
| Logs | ❌ | Placeholder "coming soon" |
| Webhooks UI | ❌ | No webhook management page |
| **Backend Infrastructure** | | |
| SQLAlchemy models (32 tables) | ✅ | All defined |
| Alembic migrations | ✅ | env.py + ini configured |
| Redis integration | ✅ | Connection pool + rate limit |
| Background tasks (7) | ✅ | Wired into lifespan |
| RBAC middleware | 🔧 | Owner check exists — no role hierarchy |
| Audit logging | ❌ | No AuditLog model in use |
| Idempotency | ❌ | No idempotency key support |
| Circuit breakers | ❌ | Not implemented |
| Retry with backoff | ❌ | Not implemented |
| Graceful shutdown | 🔧 | Exists in lifespan — not hardened |
| **Discord Bot** | ❌ | Not started |
| **Testing** | ❌ | No tests exist |
| **Deployment** | | |
| API deployed (port 8000) | ✅ | Running on 104.168.24.47 |
| Dashboard deployed (port 3000) | ✅ | Next.js running |
| nginx reverse proxy | ❌ | Not configured |
| SSL/HTTPS | ❌ | HTTP only |
| CI/CD pipeline | ❌ | Manual git push + rebuild |

---

## Table of Contents

1. [Dashboard Completion Plan](#1-dashboard-completion-plan)
   - [Sprint 1: Overview + Accounts (Week 1)](#sprint-1-overview--accounts)
   - [Sprint 2: Bots (Week 2)](#sprint-2-bots)
   - [Sprint 3: Licenses + Emails (Week 3)](#sprint-3-licenses--emails)
   - [Sprint 4: Settings + Logs + Webhooks (Week 4)](#sprint-4-settings--logs--webhooks)
   - [Sprint 5: Real-time + Polish (Week 5)](#sprint-5-real-time--polish)
2. [API Contract & Backend Gaps](#2-api-contract--backend-gaps)
3. [Infrastructure & Hardening](#3-infrastructure--hardening)
4. [Discord Bot](#4-discord-bot)
5. [Testing Strategy](#5-testing-strategy)
6. [Deployment Pipeline](#6-deployment-pipeline)
7. [Appendices](#7-appendices)

---

## 1. Dashboard Completion Plan

### Sprint 1: Overview + Accounts (Week 1)

**Goal:** Overview page shows real data, Accounts page is fully functional.

#### Overview Page — Current state & fix

```
Current:  4 stat cards loading from /health, /admin/users, /admin/licenses, /status
Problem:  /admin/users and /admin/licenses require owner role — regular user gets 403
Fix:      Create a new /dashboard/stats aggregate endpoint that returns everything in one call
```

##### Backend — New endpoint

Create `autosecure/api/routes/v1/dashboard.py`:

```python
# GET /api/v1/dashboard/stats
# Returns aggregated data for the overview page — no admin role required
# Response:
{
  "total_accounts": 1247,
  "total_bots": 12,
  "active_bots": 8,
  "total_licenses": 89,
  "active_licenses": 67,
  "total_users": 45,
  "uptime_seconds": 3600,
  "health": { "database": true, "redis": true },
  "recent_activity": [
    { "action": "account.secured", "target": "player1", "timestamp": "..." },
    ...
  ]
}
```

Register the router in `__init__.py`.

##### Frontend — Overview page rewrite

```
Required components:
1. StatsRow — 6 stat cards (Accounts, Bots Online, Users, Licenses Active, Uptime, Health)
2. HealthCard — database/redis status badges
3. RecentActivityFeed — scrollable list of recent actions
4. QuickActionButtons — shortcuts to Accounts, Bots, Licenses pages
```

**Deliverables:**
- [ ] `dashboard/app/(dashboard)/page.tsx` — rewrite to use `/api/v1/dashboard/stats`
- [ ] `dashboard/components/stats-card.tsx` — reusable stat card (icon, label, value, trend)
- [ ] `dashboard/components/activity-feed.tsx` — recent activity list
- [ ] Backend: `api/routes/v1/dashboard.py` — aggregate stats endpoint
- [ ] Register dashboard router in `__init__.py`

#### Accounts Page — Full CRUD

**Current:** Table renders with search. No create. No delete. Detail page has wrong field names.

**API response shape check:**
```python
# Actual backend response (api/models/accounts.py):
class AccountResponse(BaseModel):
    uid: str
    username: str
    email: str | None
    networth: int | None
    created_at: datetime

# What frontend expects:
interface Account {
  uuid: string;   // ❌ Backend returns "uid" not "uuid"
  ign: string;    // ❌ Backend returns "username" not "ign"
  email: string;
  status: string; // ❌ Backend doesn't have "status" field
  created_at: string;
}
```

Fix: Either align frontend types to backend response, or add fields to backend model.

##### Plan

1. **Stop building fake frontend types.** Create `dashboard/lib/types.ts` that mirrors backend Pydantic models exactly.
2. **Update AccountsPage** to match real API response (`uid`, `username`, `email`, `networth`, `created_at`).
3. **Add Add Account dialog** — modal form with uid, username, email, recovery_code fields, calls `POST /api/v1/accounts`.
4. **Add Delete account** — confirmation dialog, calls `DELETE /api/v1/accounts/{uid}`.
5. **Fix account detail page** — field names, remove fake "status" and "last_login" and "licenses" (those don't come from the API), add networth display.

**Deliverables:**
- [ ] `dashboard/lib/types.ts` — AccountResponse, BotResponse, LicenseResponse, etc.
- [ ] `dashboard/app/(dashboard)/accounts/page.tsx` — real API fields, add/delete
- [ ] `dashboard/app/(dashboard)/accounts/[id]/page.tsx` — real fields, show networth
- [ ] `dashboard/components/add-account-dialog.tsx` — modal form
- [ ] `dashboard/components/confirm-delete-dialog.tsx` — confirmation modal

---

### Sprint 2: Bots (Week 2)

**Goal:** Bot management with start, stop, restart, token editing, detail view.

#### Current state
```
Backend:
  GET /api/v1/bots — list user's bots (returns id, user_id, botnumber, status)
  GET /api/v1/bots/{id} — get one bot
  POST /api/v1/bots — create with token (body: {token: "..."})
  PUT /api/v1/bots/{id} — update domain, activity, dmmode
  DELETE /api/v1/bots/{id} — destroy bot
  POST /api/v1/bots/{id}/restart — restart bot

Frontend:
  Table renders id, botnumber, status, created_at
  "New Bot" sends {token: "pending"} — placeholder, not real
  No edit, no start/stop, no restart
  No detail page
```

#### Plan

1. **Bot list actions** — Add Start/Stop/Restart buttons per row. Start = POST (needs backend endpoint), Stop = DELETE (currently kills it), Restart = POST `{id}/restart`.
2. **Bot create modal** — Form with token field (not "pending"), show generated bot number on success.
3. **Bot detail page** — `/bots/{id}` with config editor (domain, activity, dmmode) via PUT.
4. **Backend gaps**:
   - No `POST /bots/{id}/start` endpoint (just starts from state)
   - Add `created_at` to `BotResponse` Pydantic model

**Deliverables:**
- [ ] `dashboard/app/(dashboard)/bots/page.tsx` — start/stop/restart/delete buttons, create modal
- [ ] `dashboard/app/(dashboard)/bots/[id]/page.tsx` — bot detail with config editor
- [ ] `dashboard/components/create-bot-dialog.tsx` — form with token field
- [ ] `dashboard/components/bot-status-badge.tsx` — running/stopped with color
- [ ] Backend: add `created_at` to `BotResponse` model
- [ ] Backend: add `POST /bots/{id}/start` (start a stopped bot)

---

### Sprint 3: Licenses + Emails (Week 3)

**Goal:** Full license management (generate, redeem, transfer) + email inbox with detail view.

#### Licenses — Current state
```
Backend:
  GET  /admin/licenses — list all (owner)
  POST /admin/licenses/generate — create keys (owner)
  POST /licenses/redeem — claim a key (user)
  GET  /licenses/{key}/status — check key (user)
  POST /licenses/transfer — give key to another user

Frontend:
  Read-only table of all licenses (admin endpoint)
  No generate, no redeem, no transfer
```

#### Plan

1. **License list** — Add status badges (Active/Expired/Warning) based on expiry. Add search by key/user.
2. **Generate licenses dialog** — Admin form: count, expiry duration. Calls `POST /admin/licenses/generate`.
3. **Redeem license** — User-facing form: enter key, calls `POST /licenses/redeem`. Shows result (success + expiry).
4. **Transfer license** — Inline action per license: enter target user_id, calls `POST /licenses/transfer`.
5. **Licenses page per user** — `/users/{id}/licenses` via `GET /users/{id}/licenses`.

#### Emails — Current state
```
Backend:
  GET  /emails/{address} — list emails (ownership check)
  POST /emails/watch — register address for monitoring

Frontend:
  Watch + Fetch works. No unwatch. No email detail. No real-time.
```

#### Plan

1. **Email detail** — Click an email row → expandable view showing full content (sender, subject, description, time).
2. **Unwatch email** — Add "Stop Watching" button per address that calls `DELETE /emails/watch/{address}`.
3. **Auto-refresh** — Poll `/emails/{address}` every 5s when viewing an inbox.
4. **Watched addresses list** — Show all watched addresses for the user (needs backend endpoint: `GET /emails/watched`).

**Deliverables:**
- [ ] `dashboard/app/(dashboard)/licenses/page.tsx` — generate, redeem, transfer actions
- [ ] `dashboard/components/generate-licenses-dialog.tsx` — count + expiry form
- [ ] `dashboard/components/redeem-license-dialog.tsx` — key input form
- [ ] `dashboard/components/license-status-badge.tsx` — active/warning/expired
- [ ] `dashboard/app/(dashboard)/emails/page.tsx` — detail view, unwatch, auto-refresh
- [ ] Backend: `DELETE /emails/watch/{address}` — stop watching
- [ ] Backend: `GET /emails/watched` — list watched addresses
- [ ] Backend: Add `created_at` to email list response

---

### Sprint 4: Settings + Logs + Webhooks (Week 4)

**Goal:** Fully functional settings editor, audit log viewer, webhook management.

#### Settings — Current state
```
Backend:
  GET  /users/{user_id} — profile (permissions, claiming, rest_split)
  PUT  /users/{user_id}/settings — update showleaderboard
  No config.yaml editing API

Frontend:
  Input box that fetches /users/{id} on enter. That's it.
```

#### Plan

1. **Settings form** — Load current user's profile on mount. Form fields:
   - General: claiming (text input), rest_split (number)
   - Discord preferences: showleaderboard (toggle)
   - Security: change password (new field needed in backend)
2. **Config editor (admin)** — Admin-only page to view/edit config.yaml values (whitelist safe fields: ui.*, smtp.*, etc.).
3. **Password change** — Backend: `PUT /users/{user_id}/password` with current + new password.

#### Logs — Current state
```
Backend: No audit log model. No log viewer API.
Frontend: "Coming soon" placeholder.
```

#### Plan

1. **AuditLog model** — Create `models/audit.py`:
   ```python
   class AuditLog(Base):
       __tablename__ = "audit_logs"
       id = Column(Integer, primary_key=True)
       timestamp = Column(DateTime, server_default=func.now())
       actor_id = Column(String(255), nullable=False)
       action = Column(String(100), nullable=False)
       target_type = Column(String(50))
       target_id = Column(String(255))
       details = Column(JSON)
       success = Column(Boolean, default=True)
       ip_address = Column(String(45))
   ```
2. **Audit logging middleware** — Auto-log all API requests (path, method, user_id, status, duration).
3. **Log viewer API** — `GET /admin/logs` with pagination, filter by action/actor/date, owner-only.
4. **Log viewer page** — Table with filters (action type, user, date range, success/fail).
5. **Wired into existing routes** — Add `log_audit_event()` call to every write endpoint.

#### Webhooks — Current state
```
Backend: Full CRUD exists.
Frontend: No UI at all.
```

#### Plan

1. **Webhooks page** — `/webhooks` with create form (URL, events list, secret) + list with delete.
2. **Webhook test button** — Send test event.

**Deliverables:**
- [ ] Backend: `models/audit.py` — AuditLog model
- [ ] Backend: Alembic migration for audit_logs table
- [ ] Backend: `core/audit.py` — `log_audit_event()` helper
- [ ] Backend: `GET /admin/logs` — paginated log viewer API
- [ ] Backend: `PUT /users/{user_id}/password` — change password
- [ ] Backend: `GET /emails/watched` — list watched addresses
- [ ] Backend: `DELETE /emails/watch/{address}` — stop watching
- [ ] `dashboard/app/(dashboard)/settings/page.tsx` — full settings form
- [ ] `dashboard/app/(dashboard)/logs/page.tsx` — log viewer with filters
- [ ] `dashboard/app/(dashboard)/webhooks/page.tsx` — webhook management
- [ ] `dashboard/components/logs-filter.tsx` — filter bar component
- [ ] `dashboard/components/webhook-form.tsx` — create/edit webhook form

---

### Sprint 5: Real-time + Polish (Week 5)

**Goal:** SSE for live updates, error handling, loading states, public status page.

#### SSE — Server-Sent Events

1. **Backend:** `GET /api/v1/events` — SSE endpoint that streams events from Redis pub/sub.
   ```python
   # Events emitted:
   #   account.created   — {uid, username, user_id}
   #   account.deleted   — {uid}
   #   bot.status_change — {bot_id, status, user_id}
   #   license.redeemed  — {license_key, user_id}
   #   license.expired   — {license_key}
   ```
2. **Frontend:** Hook `useEvents()` that connects to `/api/v1/events`, invalidates react-query caches on relevant events.
3. **Wired into overview** — Live bot count, recent activity feed.

#### Public Status Page

1. **`/status`** — Public page (no auth) showing:
   - API health (green/red dot)
   - Database status
   - Redis status
   - Uptime
   - Not rendering inside dashboard (different layout, no sidebar)
2. **Backend:** `GET /api/v1/public/status` — lightweight health check (no auth).

#### Polish

1. **Error boundaries** — Wrap each page in `<ErrorBoundary>` that shows "Something went wrong" with retry button.
2. **Loading skeletons** — Replace all "Loading..." text with skeleton animations.
3. **Empty states** — Consistent empty state: icon + message + action button (e.g., "No accounts yet. Add your first account.").
4. **Toast notifications** — Success/error toasts on all mutations (create, delete, update).
5. **Pagination** — All list pages use server-side pagination (page, per_page, total, pages).
6. **Keyboard shortcuts** — `Ctrl+K` for search, `Ctrl+N` for new item.
7. **Responsive sidebar** — Collapsible on mobile. Currently fixed 224px.

**Deliverables:**
- [ ] Backend: `api/routes/v1/events.py` — SSE endpoint
- [ ] Backend: Redis pub/sub on all write operations
- [ ] `dashboard/lib/hooks/useEvents.ts` — SSE subscription hook
- [ ] `dashboard/app/status/page.tsx` — public status page (no auth, no sidebar)
- [ ] `dashboard/components/error-boundary.tsx` — page-level error boundary
- [ ] `dashboard/components/skeleton.tsx` — reusable skeleton component
- [ ] `dashboard/components/empty-state.tsx` — consistent empty state
- [ ] Pagination on accounts, bots, licenses, emails, logs pages
- [ ] Toast notifications on all mutations

---

## 2. API Contract & Backend Gaps

### 2.1 Missing Endpoints

| Endpoint | Method | Purpose | Priority |
|---|---|---|---|
| `/api/v1/dashboard/stats` | GET | Aggregated dashboard overview (no auth) | High |
| `/api/v1/bots/{id}/start` | POST | Start a stopped bot | High |
| `/api/v1/emails/watched` | GET | List watched addresses | Medium |
| `/api/v1/emails/watch/{address}` | DELETE | Stop watching an address | Medium |
| `/api/v1/users/{user_id}/password` | PUT | Change password | Medium |
| `/api/v1/admin/logs` | GET | Paginated audit log viewer | High |
| `/api/v1/events` | GET | SSE real-time stream | Medium |
| `/api/v1/public/status` | GET | Lightweight public health check | Low |

### 2.2 Model Field Gaps

| Model | Missing Field | Frontend Needs It For |
|---|---|---|
| `BotResponse` | `created_at: datetime` | Bot list table |
| `AccountResponse` | `status: str` | Account status badge |
| `AccountResponse` | `last_login: datetime \| None` | Account detail |
| `EmailMessage` | `read: bool` | Read/unread indicator |
| `EmailMessage` | `created_at: datetime` | Email list timing |

### 2.3 Response Shape Mismatches (Frontend vs Backend)

**Accounts list page:**
```
Frontend uses:  { uuid, ign, email, status, created_at }
Backend sends:  { uid, username, email, networth, created_at }
Fix:           Align frontend types to backend. Map uid→uuid, username→ign in lib/types.ts
```

**Account detail page:**
```
Frontend expects: { uuid, ign, email, status, created_at, last_login, licenses: [...] }
Backend sends:    { uid, username, email, networth, created_at }
Fix:             Remove fake fields. Add networth display. Add licenses separately if needed.
```

### 2.4 RBAC — Full Role Implementation

**Current:** Only `OwnerUser` check exists. No roles, no hierarchy.

**Target permission matrix:**

```
Role       manage_users  manage_licenses  manage_bots  view_logs  view_admin  generate_licenses
───────    ────────────  ──────────────── ──────────── ────────── ─────────── ─────────────────
owner       ✓             ✓                ✓            ✓          ✓           ✓
admin       ✓             ✗                ✓ (own)      ✓          ✓           ✗
user        ✗             ✗                ✓ (own)      ✗          ✗           ✗
viewer      ✗             ✗                ✗            ✗          ✗           ✗
```

**Implementation:** Add `role` field to `User.permissions` JSON. Create middleware `require_role("admin")` that wraps `require_owner` logic but checks role hierarchy.

---

## 3. Infrastructure & Hardening

### 3.1 nginx Reverse Proxy

**Current:** API on port 8000, Dashboard on port 3000, both directly exposed with ufw.

**Target:**

```
Port 443 (HTTPS) → nginx
  ├── /api/*  → proxy_pass localhost:8000
  ├── /auth/* → proxy_pass localhost:8000
  ├── /health → proxy_pass localhost:8000
  └── /*      → proxy_pass localhost:3000 (Next.js)
```

This eliminates:
- CORS issues entirely (everything same-origin)
- Need for `NEXT_PUBLIC_API_URL`
- Need for Next.js rewrites

### 3.2 SSL/HTTPS

- Use Let's Encrypt + certbot for auto-renewing SSL
- Redirect HTTP→HTTPS at nginx level
- HSTS header

### 3.3 pm2 Process Management

**Current:** Bare `nohup npx next start` — if the process dies, it's down.

**Target:** pm2 for both API and dashboard:

```bash
pm2 start .venv/bin/uvicorn --name autosec-api -- autosecure.core.app:app --host 0.0.0.0 --port 8000
pm2 start npm --name autosec-dash --cwd /opt/autosec/dashboard -- start
pm2 save
pm2 startup
```

This gives:
- Auto-restart on crash
- Log management (pm2 logs)
- Startup on boot

### 3.4 Hardening Checklist

- [ ] nginx reverse proxy (single port 443)
- [ ] Let's Encrypt SSL (auto-renew via certbot)
- [ ] CSP headers in nginx
- [ ] HSTS header
- [ ] Rate limiting on auth endpoints (10 req/min)
- [ ] Account lockout after 5 failed login attempts
- [ ] Password complexity requirements
- [ ] Session token rotation on login
- [ ] CSRF tokens on dashboard mutations
- [ ] Input sanitization on all user-facing fields
- [ ] Audit logging on all write operations
- [ ] Idempotency keys on account/bot/license creation
- [ ] Retry with backoff on external API calls (Hypixel, MS)
- [ ] Circuit breakers on external services
- [ ] Graceful shutdown (5s timeout)
- [ ] Resource limits in pm2 (max_memory_restart)

---

## 4. Discord Bot

**Not started yet. Planned after dashboard is complete.**

### Phase 1 — Controller Bot (Week 6-7)

The main bot that handles slash commands, button interactions, and modal submissions. Runs once, manages state.

**Files to create:**
```
bot/controller/client.py           — Main bot startup, Discord client
bot/controller/events/on_ready.py  — Sync commands, start workers
bot/controller/events/on_interaction.py — Route interactions
bot/controller/commands/__init__.py — 32 slash command definitions
bot/controller/buttons/__init__.py  — 100+ button handler files
bot/controller/modals/__init__.py   — 60+ modal handler files
```

### Phase 2 — Worker Bots (Week 7-8)

Per-user bot instances that handle account securing. Each user gets their own bot instance.

**Files to create:**
```
bot/worker/client.py        — Worker bot factory class
bot/worker/query.py         — botnumber-aware DB queries
bot/worker/commands/        — 17 worker-specific commands
bot/worker/buttons/         — Worker button handlers
bot/worker/modals/          — Worker modal handlers
bot/worker/events/          — Worker event handlers
```

### Phase 3 — UI Components (Week 8)

```
ui/embeds.py       — Embed builders (account info, stats, etc.)
ui/panels.py       — Feature panels (purchase, guide, settings)
ui/modals.py       — Modal builders
ui/stats_card.py   — Stats image generation
ui/accounts.py     — Account display helpers
ui/email_viewer.py — Email display in Discord
```

---

## 5. Testing Strategy

### 5.1 Backend Tests

**Framework:** pytest + pytest-asyncio + httpx AsyncClient

**Test structure:**
```
tests/
├── conftest.py            — fixtures (db, client, auth headers)
├── test_api/
│   ├── test_auth.py       — login, refresh, logout
│   ├── test_accounts.py   — CRUD + stats
│   ├── test_bots.py       — CRUD + start/stop
│   ├── test_licenses.py   — redeem, transfer, admin generate
│   ├── test_emails.py     — watch, fetch, unwatch
│   ├── test_users.py      — profile, settings
│   ├── test_webhooks.py   — CRUD
│   └── test_admin.py      — admin-only endpoints
├── test_services/
│   ├── test_auth.py       — Microsoft auth flow
│   ├── test_hypixel.py    — Stats fetching
│   └── test_securing.py   — OTP, recovery flows
├── test_tasks/
│   ├── test_license_check.py
│   └── test_quarantine.py
└── test_db/
    ├── test_accounts.py
    └── test_bots.py
```

**Coverage target:** 80%+ on API routes, 60%+ on services.

**Key test cases per sprint:**

| Sprint | Test Coverage |
|---|---|
| Sprint 1 | Dashboard stats endpoint, account CRUD |
| Sprint 2 | Bot CRUD, start/stop lifecycle |
| Sprint 3 | License redeem/transfer/generate, email watch/unwatch |
| Sprint 4 | Audit log, settings, webhooks |
| Sprint 5 | SSE endpoint, public status |

### 5.2 Frontend Tests

**Framework:** Playwright for E2E, Vitest + React Testing Library for unit.

```
tests/e2e/
├── login.spec.ts          — Login flow, cookie, redirect
├── overview.spec.ts       — Stats load, health check display
├── accounts.spec.ts       — List, search, create, delete
├── bots.spec.ts           — List, create, start, stop, delete
├── licenses.spec.ts       — List, generate, redeem
└── settings.spec.ts       — Profile editing, password change
```

### 5.3 CI

**Current:** Nothing.

**Target:** GitHub Actions running on every push:

```yaml
name: CI
on: [push]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest --cov=autosecure
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - run: cd dashboard && npm ci && npm run build
```

---

## 6. Deployment Pipeline

### 6.1 Current Flow (manual)

```
git push origin main
ssh into server
cd /opt/autosec && git pull
cd dashboard && npm run build
kill next process && restart
```

### 6.2 Target Flow (automated)

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: 104.168.24.47
          username: root
          key: ${{ secrets.SSH_KEY }}
          script: |
            set -e
            cd /opt/autosec
            git pull origin main
            cd dashboard && npm ci && npm run build
            pm2 restart autosec-api autosec-dash
```

### 6.3 Rollback Plan

- PM2 saves process list — if a deploy fails, `pm2 resurrect` restores last working state
- VCS rollback: `git revert HEAD` or `git reset --hard <last-good-sha>` + rebuild

---

## 7. Appendices

### A. Technology Reference

| Layer | Tech | Version |
|---|---|---|
| Backend framework | FastAPI | ≥0.115 |
| ASGI server | uvicorn | ≥0.34 |
| Database | PostgreSQL 16 | — |
| ORM | SQLAlchemy async | ≥2.0 |
| Migrations | Alembic | ≥1.14 |
| Cache | Redis 8 | — |
| Frontend | Next.js | 15.x |
| Styling | Tailwind CSS | 3.4 |
| Language (backend) | Python | 3.12 |
| Language (frontend) | TypeScript | 5.x |
| Process manager | pm2 | latest |

### B. Environment Variables (.env)

```
AUTOSECURE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/autosecure
AUTOSECURE_REDIS_URL=redis://localhost:6379/0
AUTOSECURE_SECRET_KEY=<random-64-char-hex>
AUTOSECURE_SECURITY__JWT_SECRET=<random-64-char-hex>
AUTOSECURE_API_HOST=0.0.0.0
AUTOSECURE_API_PORT=8000
AUTOSECURE_API_WORKERS=4
```

### C. Quick Reference — Useful Commands

```bash
# Local dev
cd autosecure && uvicorn autosecure.core.app:app --reload --port 8000
cd dashboard && npm run dev -- --port 3000

# Server deploy
git push origin main
ssh root@104.168.24.47
cd /opt/autosec && git pull
cd dashboard && npm run build
pm2 restart all

# Server logs
tail -f /var/log/autosec-api.log
tail -f /var/log/autosec-dash.log
pm2 logs

# Database
psql -U autosecure -d autosecure
alembic upgrade head
alembic revision --autogenerate -m "description"

# Clean rebuild
rm -rf dashboard/.next && npm run build
pkill -f "next start" && npm start

# SSL
certbot --nginx -d autosecure.me
```

### D. File Tree (Completed — Target State)

```
autosec/
├── autosecure/
│   ├── core/              # App factory, config, DB, Redis, state, logging
│   ├── models/            # 32 SQLAlchemy models
│   ├── db/                # Repository classes (12)
│   ├── api/
│   │   ├── auth.py        # JWT auth endpoints
│   │   ├── models/        # Pydantic schemas
│   │   └── routes/v1/     # All route modules (11 files)
│   ├── services/          # Business logic (MS auth, Hypixel, etc.)
│   ├── tasks/             # Background tasks (7)
│   ├── bot/               # Discord bot (controller + worker)
│   ├── ui/                # Discord embed builders
│   └── utils/             # Generators, validators, HTTP helpers
├── dashboard/
│   ├── app/
│   │   ├── (dashboard)/   # Pages with sidebar (8 pages)
│   │   ├── login/         # Auth page (no sidebar)
│   │   ├── status/        # Public status page (no auth, no sidebar)
│   │   ├── layout.tsx     # Root layout
│   │   └── providers.tsx  # QueryClient + toast
│   ├── components/
│   │   ├── ui/            # shadcn-style primitives (Card, Button, etc.)
│   │   ├── sidebar.tsx    # Navigation
│   │   └── *.tsx          # Feature components
│   └── lib/
│       ├── api.ts         # API client
│       ├── types.ts       # TypeScript types
│       └── hooks/         # TanStack Query hooks
├── DEVELOPMENT_PLAN.md    # This file
├── config.yaml            # Server config
└── pyproject.toml         # Python project config
```
