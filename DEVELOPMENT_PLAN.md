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
| JWT auth (login/refresh/logout) | ✅ | Works — deps injection fixed |
| Health check | ✅ | Returns DB + Redis status |
| Account CRUD | ✅ | List, get, create, delete — empty DB |
| Bot CRUD | ✅ | List, get, create, update, delete — empty DB |
| License redeem/transfer/status | ✅ | User endpoints work |
| Admin users (list/delete) | ✅ | Owner-only, returns round@autosecure.me |
| Admin licenses (list/generate) | ✅ | Owner-only, empty DB |
| Email inbox + watch | 🔧 | Watch works, fetch works — no unwatch, no watched-list |
| Webhook subscriptions | ✅ | CRUD with ownership check |
| User profile + settings | ✅ | View own profile, update settings |
| SSE events endpoint | ❌ | Not implemented |
| Dashboard stats aggregate | ❌ | Not implemented |
| Public status page | ❌ | Not implemented |
| **Frontend Dashboard** | | |
| Login page | ✅ | JWT + cookie, no sidebar, works |
| Overview page | 🔧 | 4 stat cards hit working API — shapes mismatch |
| Accounts list | 🔧 | Table renders, search works — no add/delete UI |
| Account detail | 🔧 | Renders card — field names mismatch API |
| Bots list | 🔧 | Table + create/delete — token placeholder |
| Bot detail | ❌ | No bot detail/edit page |
| Bot start/stop/restart | ❌ | No action buttons |
| Licenses list | 🔧 | Read-only table — no generate/redeem/transfer |
| Email inbox | 🔧 | Watch + fetch work — no unwatch, no detail |
| Settings | ❌ | Empty input box — no settings editing |
| Logs | ❌ | Placeholder "coming soon" |
| Webhooks UI | ❌ | No webhook management page |
| **Backend Infrastructure** | | |
| SQLAlchemy models (32 tables) | ✅ | All defined |
| Alembic migrations | ✅ | env.py + ini configured |
| Redis integration | ✅ | Connection pool + rate limit |
| Background tasks (7) | ✅ | Wired into lifespan |
| RBAC (owner check) | 🔧 | Config list + DB role fallback — no role hierarchy |
| Audit logging | ❌ | No AuditLog model or viewer API |
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

## Critical Fixes Applied (2026-07-29)

### Bug 1: All authenticated endpoints returned 422
**Root cause:** Every route file imported `CurrentUser`, `DBSession`, `OwnerUser` inside `if TYPE_CHECKING:` blocks. `TYPE_CHECKING` is `False` at runtime, so FastAPI never saw the `Depends()` markers. It treated `user_id` and `db` as query parameters.

**Fix:** Moved imports outside `TYPE_CHECKING` across 8 route files.

### Bug 2: Pydantic models "not fully defined"
**Root cause:** `accounts.py` and `bots.py` API models imported `datetime` under `TYPE_CHECKING`. With `from __future__ import annotations`, `datetime` was an undefined string at runtime, and Pydantic couldn't resolve `datetime.datetime | None`.

**Fix:** Import `datetime` at runtime (real import, not TYPE_CHECKING).

### Bug 3: Owner check always failed
**Root cause:** `require_owner()` only checked `settings.owners` (config.yaml), which was `['']` (empty string). The user `round@autosecure.me` had `role: owner` in DB permissions but the config list was blank.

**Fix:** Added user to config.yaml owners list. Enhanced `require_owner()` to fall back to checking `user.permissions.role == "owner"` from the database.

### Bug 4: Login page had sidebar; redirect loop
**Root cause:** Root layout had `<Sidebar />` for ALL pages. Login page used direct cross-origin fetch to `:8000`. Overview page API calls (also cross-origin) got 401 and redirected back to `/login`.

**Fix:** Restructured with route groups (sidebar in `(dashboard)` group). Proxied `/auth/*` through Next.js. Made login use relative URL. Middleware excludes `/auth` paths.

---

## Sprint-Based Development Plan

### Sprint 1: Overview + Accounts (Week 1)

**Goal:** Overview page shows real data, Accounts page is fully functional.

#### Overview Page

**Current:** 4 stat cards hitting `/health`, `/admin/users`, `/admin/licenses`, `/status`. These work now but don't give a complete picture.

**Required:**
- [ ] Backend: Create `GET /api/v1/dashboard/stats` — aggregate endpoint returning:
  ```json
  {
    "total_accounts": 0,
    "total_bots": 0,
    "active_bots": 0,
    "total_licenses": 0,
    "active_licenses": 0,
    "total_users": 1,
    "uptime_seconds": 3600,
    "health": {"database": true, "redis": true},
    "recent_activity": []
  }
  ```
- [ ] Backend: Register `dashboard.py` router in `__init__.py`
- [ ] Frontend: Rewrite Overview page to use `/api/v1/dashboard/stats`
- [ ] Frontend: Create `stats-card.tsx` — reusable stat card (icon, label, value)
- [ ] Frontend: Create `activity-feed.tsx` — recent activity list
- [ ] Frontend: Quick Action buttons → Accounts, Bots, Licenses

#### Accounts Page

**Backend `AccountResponse` actual shape:**
```python
{ uid, username, email, networth, created_at }
```

**Frontend current `interface Account` (WRONG):**
```typescript
{ uuid, ign, email, status, created_at }
```

**Required:**
- [ ] Frontend: Create `dashboard/lib/types.ts` — mirror all Pydantic models:
  ```typescript
  export interface AccountResponse {
    uid: string;
    username: string;
    email: string | null;
    networth: number | null;
    created_at: string;
  }
  export interface AccountListResponse {
    accounts: AccountResponse[];
    total: number;
    page: number;
    pages: number;
  }
  export interface BotResponse {
    id: number;
    user_id: string;
    botnumber: number;
    status: string;
    created_at: string | null;
  }
  export interface LicenseResponse {
    license_key: string;
    user_id: string;
    expires_at: string;
    is_active: boolean;
  }
  export interface AdminLicenseResponse {
    license_key: string;
    user_id: string | null;
    expires_at: string;
    is_used: boolean;
  }
  export interface AdminUserResponse {
    user_id: string;
    permissions: Record<string, any>;
    claiming: string;
    rest_split: number;
  }
  export interface UserProfileResponse {
    user_id: string;
    permissions: Record<string, any>;
    claiming: string;
    rest_split: number;
  }
  export interface EmailMessage {
    id: number;
    sender: string;
    subject: string;
    description: string;
    time: number;
  }
  export interface WebhookResponse {
    id: number;
    url: string;
    events: string[];
    active: boolean;
  }
  export interface HealthResponse {
    status: string;
    checks: Record<string, boolean>;
    uptime: number;
  }
  export interface DashboardStats {
    total_accounts: number;
    total_bots: number;
    active_bots: number;
    total_licenses: number;
    active_licenses: number;
    total_users: number;
    uptime_seconds: number;
    health: Record<string, boolean>;
    recent_activity: any[];
  }
  ```
- [ ] Frontend: Rewrite Accounts list page — use real field names (uid, username, email, networth)
- [ ] Frontend: Add "Add Account" dialog — form: uid, username, email, recovery_code → `POST /api/v1/accounts`
- [ ] Frontend: Add "Delete" button per row — confirmation dialog → `DELETE /api/v1/accounts/{uid}`
- [ ] Frontend: Fix Account detail page — remove fake `status`/`last_login`/`licenses`, add networth display

---

### Sprint 2: Bots (Week 2)

**Goal:** Full bot lifecycle management.

**Backend routes (all verified working):**
```
GET    /api/v1/bots          → list user's bots
GET    /api/v1/bots/{id}     → get bot details
POST   /api/v1/bots          → create with {token}
PUT    /api/v1/bots/{id}     → update domain, activity, dmmode
DELETE /api/v1/bots/{id}     → destroy bot
POST   /api/v1/bots/{id}/restart → restart bot
```

**Required:**
- [ ] Backend: Add `created_at` field to `BotResponse` Pydantic model (already in code but verify it's populated)
- [ ] Backend: Add `POST /api/v1/bots/{id}/start` — start a stopped bot
- [ ] Frontend: Bot list page — action buttons per row: Start, Stop, Restart, Delete
- [ ] Frontend: Create bot modal — form with real token field (not `"pending"`)
- [ ] Frontend: Bot detail page at `/bots/{id}` — config editor (domain, activity, dmmode) via PUT

---

### Sprint 3: Licenses + Emails (Week 3)

**Goal:** Full license management (generate, redeem, transfer) + email inbox with detail.

#### Licenses

**Backend routes (all working):**
```
GET    /api/v1/admin/licenses        → list all (owner)
POST   /api/v1/admin/licenses/generate → create keys (owner)
POST   /api/v1/licenses/redeem       → claim key (user)
GET    /api/v1/licenses/{key}/status → check key (user)
POST   /api/v1/licenses/transfer     → transfer to another user
```

**Required:**
- [ ] Frontend: License list — add status badges (Active/Expired/Warning based on expiry)
- [ ] Frontend: "Generate Licenses" dialog (admin) — count + expiry, calls admin generate
- [ ] Frontend: "Redeem License" dialog (user) — enter key, calls redeem
- [ ] Frontend: "Transfer" button per license — enter target user_id, calls transfer
- [ ] Frontend: Search/filter by key or user

#### Emails

**Backend routes (partially working):**
```
GET    /api/v1/emails/{address}       → list emails (works)
POST   /api/v1/emails/watch           → register address (works)
GET    /api/v1/emails/watched         → ❌ NOT IMPLEMENTED
DELETE /api/v1/emails/watch/{address} → ❌ NOT IMPLEMENTED
```

**Required:**
- [ ] Backend: `GET /api/v1/emails/watched` — list watched addresses for current user
- [ ] Backend: `DELETE /api/v1/emails/watch/{address}` — stop watching an address
- [ ] Frontend: Email detail — click row → expand showing full sender/subject/description
- [ ] Frontend: Unwatch button per watched address
- [ ] Frontend: Auto-refresh inbox (poll every 5s when viewing)

---

### Sprint 4: Settings + Logs + Webhooks (Week 4)

**Goal:** Fully functional settings editor, audit log viewer, webhook management.

#### Settings

**Backend routes (user profile works):**
```
GET  /api/v1/users/{user_id}          → profile (works)
PUT  /api/v1/users/{user_id}/settings → update showleaderboard (works)
```

**Required:**
- [ ] Backend: `PUT /api/v1/users/{user_id}/password` — change password (current + new)
- [ ] Frontend: Settings page — auto-load current user profile on mount, editable form
- [ ] Frontend: Password change form (current password, new password, confirm)
- [ ] Frontend: Claiming preference (dropdown: none/auto/manual)
- [ ] Frontend: rest_split field (number input)
- [ ] Frontend: showleaderboard toggle

#### Logs

**Backend: No audit log infrastructure. Need to build from scratch.**

**Required:**
- [ ] Backend: Create `autosecure/models/audit.py` — AuditLog model:
  ```python
  class AuditLog(Base):
      __tablename__ = "audit_logs"
      id = Column(Integer, primary_key=True)
      timestamp = Column(DateTime, server_default=func.now(), index=True)
      actor_id = Column(String(255), nullable=False, index=True)
      action = Column(String(100), nullable=False, index=True)
      target_type = Column(String(50))
      target_id = Column(String(255))
      details = Column(JSON)
      success = Column(Boolean, default=True)
      ip_address = Column(String(45))
  ```
- [ ] Backend: Alembic migration for `audit_logs` table
- [ ] Backend: Create `autosecure/core/audit.py` — `log_audit_event()` helper
- [ ] Backend: Create `GET /api/v1/admin/logs` — paginated log viewer (owner-only)
  - Query params: page, per_page, action, actor_id, target_type, success, date_from, date_to
  - Returns: `{ logs: [...], total, page, pages }`
- [ ] Backend: Wire audit logging into existing write endpoints (account create/delete, bot create/delete, license redeem/generate, login, etc.)
- [ ] Frontend: Logs page — table with filters: action type dropdown, user search, date range picker, success/fail toggle
- [ ] Frontend: Pagination on logs

#### Webhooks

**Backend routes (all working):**
```
GET    /api/v1/webhooks         → list (works)
POST   /api/v1/webhooks         → create (works)
DELETE /api/v1/webhooks/{id}    → delete (works)
```

**Required:**
- [ ] Frontend: Webhooks page at `/webhooks`
- [ ] Frontend: Create webhook form — URL, events (checkboxes), secret
- [ ] Frontend: Webhook list with delete button
- [ ] Frontend: "Test" button that fires a test event

---

### Sprint 5: Real-time + Polish (Week 5)

**Goal:** SSE for live updates, error handling, loading states, public status page.

#### SSE — Server-Sent Events

- [ ] Backend: Redis pub/sub helper — `await redis.publish("events", json.dumps(event))`
- [ ] Backend: `GET /api/v1/events` — SSE endpoint streaming from Redis pub/sub
  ```python
  @router.get("/events")
  async def event_stream(user_id: CurrentUser):
      async def generate():
          pubsub = redis.pubsub()
          await pubsub.subscribe("events")
          async for msg in pubsub.listen():
              if msg["type"] == "message":
                  yield f"data: {msg['data']}\n\n"
      return StreamingResponse(generate(), media_type="text/event-stream")
  ```
- [ ] Backend: Emit events from write endpoints:
  - `account.created`, `account.deleted`
  - `bot.created`, `bot.deleted`, `bot.status_change`
  - `license.redeemed`, `license.generated`
- [ ] Frontend: `dashboard/lib/hooks/useEvents.ts` — SSE subscription hook that invalidates react-query caches
- [ ] Frontend: Wire into overview (live bot count, recent activity feed)

#### Public Status Page

- [ ] Backend: `GET /api/v1/public/status` — lightweight health (no auth):
  ```json
  { "status": "ok", "uptime": 3600, "database": true, "redis": true }
  ```
- [ ] Frontend: `app/status/page.tsx` — public page, no auth, no sidebar
  - Green/red dot for API status
  - Database + Redis status
  - Uptime display
  - Different layout than dashboard (no sidebar, no header)

#### Polish

- [ ] Frontend: Error boundaries — wrap each page in `<ErrorBoundary>` with retry button
- [ ] Frontend: Loading skeletons — replace all "Loading..." text with animated skeleton
- [ ] Frontend: Empty states — consistent pattern: icon + message + action button
- [ ] Frontend: Toast notifications — success/error toasts on all mutations (create, delete, update)
- [ ] Frontend: Pagination — accounts, bots, licenses, emails, logs pages use server-side pagination
- [ ] Frontend: Sidebar — collapsible on mobile, active route highlighting

---

## API Contract (Real Shape vs Frontend Assumptions)

### Backend Response Shapes (What the API actually returns)

| Endpoint | Actual Fields | Notes |
|---|---|---|
| `GET /api/v1/accounts` | `{ accounts: [...], total, page, pages }` | Each account: `uid, username, email, networth, created_at` |
| `GET /api/v1/accounts/{uid}` | `{ uid, username, email, networth, created_at }` | No `status`, no `last_login`, no `licenses` |
| `POST /api/v1/accounts` | `{ uid, username, email, created_at }` | Body: `{ uid, username, email, recovery_code }` |
| `DELETE /api/v1/accounts/{uid}` | `{ success, message }` | |
| `GET /api/v1/bots` | `[ { id, user_id, botnumber, status } ]` | No `created_at` |
| `POST /api/v1/bots` | `{ id, user_id, botnumber, status }` | Body: `{ token }` |
| `DELETE /api/v1/bots/{id}` | `{ success, message }` | |
| `GET /api/v1/admin/users` | `{ users: [...], total }` | Each user: `user_id, permissions, claiming, rest_split` |
| `GET /api/v1/admin/licenses` | `{ licenses: [...], total }` | Each license: `license_key, user_id, expires_at, is_used` |
| `POST /api/v1/admin/licenses/generate` | `{ licenses: [...], count }` | Body: `{ count, expiry }` |
| `POST /api/v1/licenses/redeem` | `{ license_key, user_id, expires_at, is_active }` | Body: `{ license_key }` |
| `POST /api/v1/licenses/transfer` | `{ license_key, user_id, expires_at, is_active }` | Body: `{ new_user_id }` |
| `GET /api/v1/emails/{address}` | `{ emails: [...], total }` | Each email: `id, sender, subject, description, time` |
| `POST /api/v1/emails/watch` | `{ success, message }` | Body: `{ email }` |
| `GET /api/v1/users/{user_id}` | `{ user_id, permissions, claiming, rest_split }` | Ownership-scoped |
| `PUT /api/v1/users/{user_id}/settings` | `{ user_id, showleaderboard }` | Body: `{ showleaderboard }` |
| `GET /api/v1/webhooks` | `{ webhooks: [...], total }` | Each webhook: `id, url, events, active` |
| `POST /api/v1/webhooks` | `{ id, url, events, active }` | Body: `{ url, events, secret }` |
| `POST /auth/login` | `{ access_token, refresh_token, token_type, expires_in }` | Body: `{ email, password }` |
| `GET /health` | `{ status, checks: { database, redis }, uptime }` | No auth required |

### Missing Backend Endpoints

| Endpoint | Method | Priority | Sprint |
|---|---|---|---|
| `/api/v1/dashboard/stats` | GET | High | 1 |
| `/api/v1/bots/{id}/start` | POST | High | 2 |
| `/api/v1/emails/watched` | GET | Medium | 3 |
| `/api/v1/emails/watch/{address}` | DELETE | Medium | 3 |
| `/api/v1/users/{user_id}/password` | PUT | Medium | 4 |
| `/api/v1/admin/logs` | GET | High | 4 |
| `/api/v1/events` | GET | Medium | 5 |
| `/api/v1/public/status` | GET | Low | 5 |

---

## Infrastructure & Hardening

### 6-Item Deployment Upgrade

| # | Task | Current | Target |
|---|---|---|---|
| 1 | Process manager | Bare `nohup` processes | pm2 with auto-restart |
| 2 | Reverse proxy | Two ports (3000 + 8000) | nginx on port 443 → proxy |
| 3 | SSL | HTTP only | Let's Encrypt via certbot |
| 4 | Dashboard startup | Manual restart after build | pm2 startup script |
| 5 | API startup | Manual after kill | pm2 + auto-restart |
| 6 | CI/CD | Manual git pull + build | GitHub Actions auto-deploy |

### nginx Config (Target)

```nginx
server {
    listen 443 ssl;
    server_name autosecure.me;

    ssl_certificate /etc/letsencrypt/live/autosecure.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/autosecure.me/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /auth/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
    }
}

server {
    listen 80;
    server_name autosecure.me;
    return 301 https://$server_name$request_uri;
}
```

### Hardening Checklist

- [ ] nginx reverse proxy (single port 443)
- [ ] Let's Encrypt SSL (auto-renew via certbot)
- [ ] CSP headers in nginx
- [ ] HSTS header
- [ ] Rate limiting on auth endpoints (10 req/min via Redis)
- [ ] Account lockout after 5 failed login attempts
- [ ] Password complexity requirements
- [ ] Audit logging on all write operations
- [ ] pm2 with max memory restart (500MB per process)

---

## Discord Bot

**Not started. Planned after Sprint 5 (dashboard complete).**

Phases:
1. Controller bot — slash commands, buttons, modals (Week 6-7)
2. Worker bots — per-user bot instances (Week 7-8)
3. UI components — embeds, panels, modals (Week 8)

---

## Testing Strategy

### Phase 1: API Tests (pytest + httpx)

Start with Sprint 1. Each new endpoint gets a test.

```python
# tests/conftest.py — test DB, test client, auth headers
# tests/test_api/test_auth.py — login, refresh, logout
# tests/test_api/test_accounts.py — CRUD
# tests/test_api/test_dashboard.py — stats endpoint
```

### Phase 2: Frontend Tests (Playwright)

Start in Sprint 5. Critical flows only.

```typescript
// tests/e2e/login.spec.ts — login flow
// tests/e2e/accounts.spec.ts — list, create, delete
// tests/e2e/bots.spec.ts — list, create, delete
```

---

## Project File Tree (Completed — Target)

```
autosec/
├── autosecure/
│   ├── core/              # App factory, config, DB, Redis, state, logging, deps
│   ├── models/            # 32 SQLAlchemy models
│   ├── db/                # Repository classes (12)
│   ├── api/
│   │   ├── auth.py        # JWT auth
│   │   ├── health.py      # Health endpoint
│   │   ├── models/        # Pydantic schemas (7 files)
│   │   └── routes/v1/     # Route modules (9 files)
│   ├── services/          # Business logic
│   ├── tasks/             # Background tasks (7)
│   ├── bot/               # Discord bot (not started)
│   └── utils/             # Generators, validators
├── dashboard/
│   ├── app/
│   │   ├── (dashboard)/   # Sidebar pages (8)
│   │   ├── login/         # Auth page
│   │   ├── status/        # Public status page (Sprint 5)
│   │   ├── layout.tsx     # Root layout (html/body/providers)
│   │   └── providers.tsx
│   ├── components/
│   │   └── ui/            # shadcn-style primitives
│   └── lib/
│       ├── api.ts         # API client
│       └── types.ts       # TypeScript types (Sprint 1)
├── DEVELOPMENT_PLAN.md
├── config.yaml
└── pyproject.toml
```
