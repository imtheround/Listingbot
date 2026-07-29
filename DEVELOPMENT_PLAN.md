# AutoSecure — Development Plan

> Complete guide for translating the JS codebase to Python, optimizing it,
> making it enterprise-grade, and website-ready.

## Current Status (2026-07-28)

| Layer | Status |
|---|---|
| Models (32 SQLAlchemy tables) | Done |
| Config system (YAML + Pydantic) | Done |
| Database (PostgreSQL + Alembic) | Done |
| Redis integration | Done |
| FastAPI app lifecycle + lifespan | Done |
| API routes (33 endpoints) | Done |
| API auth (JWT login/refresh/logout) | Done |
| Background tasks (7 tasks in APScheduler) | Done |
| Admin dashboard (Next.js 15) | Done |
| RBAC middleware | Partial |
| Audit logging | Pending |
| Discord bot integration | Pending |
| Deployed to production | Done (104.168.24.47) |

**Running:** API on `:8000`, Dashboard on `:3000` — both behind ufw firewall with CORS configured.

---

## Table of Contents

1. [Translation Strategy](#1-translation-strategy)
2. [Code Optimization](#2-code-optimization)
3. [Enterprise Features](#3-enterprise-features)
4. [Website / Dashboard](#4-website--dashboard)
5. [Development Phases](#5-development-phases)
6. [Detailed File Mapping](#6-detailed-file-mapping)
7. [Quality Standards](#7-quality-standards)

---

## 1. Translation Strategy

### 1.1 What Stays the Same

- The **business logic** — securing flows, MS auth, XBL, Hypixel stats, ban checks, email handling, invoice system, quarantine, cosmetics. These are algorithmic and translate 1:1.
- The **data model** — 30+ SQLite tables become 30+ SQLAlchemy models on PostgreSQL.
- The **Discord interaction pattern** — commands, buttons, modals, events. Same concept, different library.

### 1.2 What Changes Fundamentally

| JS Pattern | Python Equivalent | Why Better |
|---|---|---|
| `require()` / `module.exports` | Python imports / packages | Enforced module boundaries, no circular deps |
| Callback-based async (`async/await` + Promises) | Native `async/await` + `asyncio` | True concurrency, no event loop blocking |
| `discord.js` v14 | `discord.py` v2.x | Same features, better type hints, native async |
| `sqlite3` (sync, callback-based) | `SQLAlchemy async` + `asyncpg` | Connection pooling, async, type-safe queries |
| `node-fetch` / `axios` | `httpx` (async) | Native async, connection pooling, retry built-in |
| `express` / `http` | `FastAPI` | Auto OpenAPI docs, DI, validation, async |
| `smtp-server` | `aiosmtpd` | Async SMTP, same API surface |
| `pm2` | `systemd` | Native Linux process management, auto-restart |
| JSON config | YAML + Pydantic Settings | Typed, validated, nested, env overrides |
| `cheerio` | `beautifulsoup4` / `lxml` | Same HTML parsing, better selectors |
| `canvas` (Node) | `Pillow` (Python) | More mature, better image manipulation |
| `playwright` (Node) | `playwright` (Python) | Same API, Python-native |
| `bip39` + `bitcoinjs-lib` | `bip39` + `ecdsa` + `mnemonic` | Same crypto, Python ecosystem |
| `chalk` / `cli-color` | `rich` / `structlog` | Better terminal output, structured logging |

### 1.3 Translation Rules

1. **Every JS file gets ONE Python file.** No more, no less. The 60+ duplicate files get consolidated.
2. **Every `queryParams()` call becomes a typed repository method.** No raw SQL in business logic.
3. **Every `require()` dependency becomes an import from a defined module.** No relative imports crossing layer boundaries.
4. **Every callback becomes an `async def`.** No blocking I/O anywhere.
5. **Every magic string becomes a constant or enum.** No hardcoded URLs, channel IDs, or magic numbers.
6. **Every inline embed builder becomes a function in `ui/`.** No embed construction in business logic.
7. **Every `console.log` becomes `structlog`.** Structured, searchable, level-filtered.

---

## 2. Code Optimization

### 2.1 Duplication Elimination

**Current state:** 20 duplicated file types across 60+ copies.

| Duplicated File | Copies | Python Solution |
|---|---|---|
| `generate.js` | 5 | `utils/generate.py` — single module |
| `modalBuilder.js` | 5 | `ui/modals.py` — single builder |
| `randomColor.js` | 3 | `utils/colors.py` — single function |
| `validEmail.js` | 3 | `utils/validators.py` — single validator |
| `embedWrapper.js` | 3 | `ui/embeds.py` — single wrapper |
| `getFiles.js` | 2 | `utils/discovery.py` — single loader |
| `getButtons.js` | 2 | `utils/discovery.py` — consolidated |
| `getModals.js` | 2 | `utils/discovery.py` — consolidated |
| `login.js` | 2 (diverged) | `services/microsoft/auth.py` — merge best of both |
| `getLiveData.js` | 2 | `services/microsoft/_http.py` — single module |
| `checkToken.js` | 2 | `utils/http.py` — single function |
| `getLocalCmds.js` | 2 | `utils/discovery.py` — consolidated |
| `extractCode.js` | 2 | `services/email/code_extractor.py` — single module |
| `emailMsg.js` | 2 (diverged) | `ui/email_viewer.py` — merge best of both |
| `otpSecure.js` | 2 (diverged) | `services/securing/otp.py` — single flow |
| `recsecure.js` | 2 (diverged) | `services/securing/recovery.py` — single flow |
| `secure.js` | 2 (diverged) | `bot/commands/secure.py` — single command |
| `email.js` | 2 (diverged) | `bot/commands/mail.py` — single command |
| `sendott.js` | 2 (both stubs) | **DELETED** — dead code |
| `test.js` / `test2.js` / `testdraw.js` | 3 | **DELETED** — test files, not production |

**Net result:** ~60 files → ~15 files. 75% reduction.

### 2.2 God File Breakup

**Current worst offenders:**

| File | Lines | Problem | Python Solution |
|---|---|---|---|
| `access.js` | 650 | Admin commands, licensing, blacklisting, transfer, DM, modals all in one | Split into `api/admin.py`, `db/licenses.py`, `services/licensing.py` |
| `helpers.js` | 905 | UUID extraction, country codes, language data, timing, captcha, gamertag | Split into `utils/countries.py`, `utils/languages.py`, `services/captcha.py`, `utils/gamertag.py`, `utils/text.py` |
| `messager.js` | 945 | Discord messages, DB queries, UUID fetching, user hiding, channel sending | Split into `ui/accounts.py`, `db/accounts.py`, `services/hypixel/resolve.py` |
| `getData.js` | 660 | Hypixel API, profile extraction, stats formatting | Split into `services/hypixel/client.py`, `services/hypixel/stats.py`, `services/hypixel/skyblock.py` |
| `quarantinehandler.js` | 612 | Quarantine logic, bot lifecycle, DB, timers, embeds | Split into `services/quarantine.py`, `tasks/quarantine_check.py`, `ui/quarantine.py` |
| `getCredentials.js` | 516 | HTTP, credential parsing, TOTP, cookies | `services/microsoft/auth.py` — clean auth flow |
| `bancheck.js` | 515 | Ban check, HTTP, DB, embeds, enforcement | `services/minecraft/bancheck.py`, `services/banning.py` |
| `recodesecure.js` | 514 | Securing, credentials, SSID, profile changes, notifications | `services/securing/recovery.py` + `services/securing/after.py` |
| `encryptOtt2.js` | 512 | Encryption, HTTP, auth flow | `services/microsoft/auth.py` — clean flow |
| `listSettings.js` | 492 | DB queries, embed building, button construction | `ui/panels.py` + `db/settings.py` |
| `db.js` | 528 | Schema, API key, init, scheduling, startup | `models/` + `db/` + `core/database.py` |
| `buttonhandlerautosec.js` | 445 | 15+ feature toggles in one switch/case | `bot/worker/buttons/` — one file per toggle |
| `multiplayerhandler.js` | 415 | OAuth, XBL, HTTP, Xbox API — hardcoded URLs | `services/minecraft/multiplayer.py` — clean with config URLs |
| `aftersecure.js` | 413 | Post-secure, retry, embeds, notifications | `services/securing/after.py` + `ui/embeds.py` |
| `login.js` | 365 | Login with 5 branches, 8 PPFT fallbacks, cookie parsing | `services/microsoft/auth.py` — clean state machine |
| `recsecure.js` | 315 | Modal, login, securing, embeds, DB | `services/securing/recovery.py` + `bot/modals/secure/` |
| `donutstats.js` | 290 | Mojang API, DonutSMP API, embeds, stats | `services/hypixel/stats.py` + `ui/stats.py` |

**Rule:** No file exceeds 200 lines. If it does, split by concern.

### 2.3 Dead Code Removal

| File | Reason | Action |
|---|---|---|
| `sendott.js` (both copies) | Returns `null` everywhere | DELETE |
| `test.js` | Empty function `test(t1,t2,amsc){}` | DELETE |
| `test2.js` | Test script importing `api.js` | DELETE |
| `testdraw.js` | Test for image generation | DELETE |
| `testxbl.js` | Has hardcoded auth token | DELETE |
| `combined.js` | Empty object `{}` | DELETE |
| `launcher_accounts.json` | Empty `{"accounts":{}}` | DELETE |
| `email_reccode.txt` | Actually JS code, duplicate of `formatAccounts.js` | DELETE |
| Commented-out code in `login.js` lines 356-364 | Hardcoded test credentials | STRIP |

### 2.4 Security Fixes

| Issue | Location | Fix |
|---|---|---|
| SQL injection | `mainbot/utils/emails/emailMsg.js:54` | Parameterized queries via SQLAlchemy |
| Global prototype mutation | `randomColor.js` (3 copies) — `String.prototype.toHex` | Eliminated entirely |
| Hardcoded auth tokens | `testxbl.js:4`, `login.js:356-364` | Deleted / stripped |
| Plaintext credentials in DB | All account tables | AES-256 encryption via `cryptography.fernet` |
| No CSRF protection | Dashboard forms | CSRF tokens on all POST forms |
| No rate limiting | Bot commands, API | Per-user rate limits via Redis |

### 2.5 Hardcoded Values → Config

| Category | Current (hardcoded) | Python (config.yaml) |
|---|---|---|
| MS login URLs | 6+ occurrences of `login.live.com` URLs | `microsoft.auth_url` |
| Xbox redirect URIs | 3 occurrences of `xbox.com/auth/msa/blank.html` | `microsoft.redirect_uri` |
| User-Agent strings | 74 occurrences across 25+ files, different versions | `http.user_agents` list (rotated) |
| API base URLs | `api.donutsmp.net`, `mctiers.com/api` | `apis.donutsmp`, `apis.mctiers` |
| SMTP port | `25` hardcoded | `smtp.port` |
| SMPT reconnect delay | `5000` ms | `smtp.reconnect_delay_ms` |
| Email code regex | `6,7` digit patterns | `email.code_length` |
| Email poll intervals | `1000`, `10000` ms | `email.poll_interval_ms`, `email.watch_timeout_ms` |
| Leaderboard update interval | `30000` ms | `tasks.leaderboard_interval_ms` |
| Invoice check interval | `60000` ms | `tasks.invoice_interval_ms` |
| Discord CDN URLs | 10+ hardcoded image URLs | `ui.thumbnail_url`, `ui.banner_url` |
| Channel IDs | `1460894741431451676`, `1461036964538089534` | `discord.channels.*` |
| Guild ID | From config but scattered | `discord.guild_id` (single source) |

---

## 3. Enterprise Features

### 3.1 Security Layer

#### Encryption at Rest

```python
# All sensitive fields encrypted before DB write, decrypted on read
ENCRYPTED_FIELDS = [
    "email", "password", "recovery_code", "secret_key",
    "ssid", "msauth_cookie", "totp_secret"
]

# Implementation: SQLAlchemy TypeDecorator
from cryptography.fernet import Fernet

class EncryptedString(TypeDecorator):
    """Encrypts/decrypts string fields automatically."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None: return None
        return Fernet(ENCRYPTION_KEY).encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None: return None
        return Fernet(ENCRYPTION_KEY).decrypt(value.encode()).decode()
```

#### Role-Based Access Control (RBAC)

```
Roles:
  owner    — Full system access, can manage all users/bots/licenses
  admin    — Can manage users, view logs, moderate
  user     — Standard license holder, manages own bots/accounts
  viewer   — Read-only access to own data

Permission Matrix:
  action                    owner  admin  user  viewer
  ────────────────────────  ─────  ─────  ────  ──────
  manage_users              ✓      ✓      ✗     ✗
  manage_licenses           ✓      ✗      ✗     ✗
  manage_bots (all)         ✓      ✗      ✗     ✗
  manage_bots (own)         ✓      ✓      ✓     ✗
  view_accounts (all)       ✓      ✓      ✗     ✗
  view_accounts (own)       ✓      ✓      ✓     ✗
  view_logs                 ✓      ✓      ✗     ✗
  manage_blacklist          ✓      ✓      ✗     ✗
  redeem_license            ✓      ✓      ✓     ✗
  view_dashboard            ✓      ✓      ✓     ✓
  manage_webhooks           ✓      ✗      ✗     ✗
  generate_licenses         ✓      ✗      ✗     ✗
  transfer_license          ✓      ✗      ✓     ✗
```

#### Audit Logging

```python
# Immutable audit trail — every significant action logged
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    actor_id = Column(String, nullable=False)       # Discord user ID or "system"
    actor_ip = Column(String)                        # Request IP
    action = Column(String, nullable=False)          # "license.redeem", "account.delete", etc.
    target_type = Column(String)                     # "user", "account", "bot", "license"
    target_id = Column(String)                       # ID of the target
    details = Column(JSONB)                          # Arbitrary metadata
    success = Column(Boolean, default=True)
    error_message = Column(String)

# Actions tracked:
# auth.login, auth.logout, auth.refresh
# license.redeem, license.transfer, license.extend, license.revoke
# account.secure, account.delete, account.view
# bot.create, bot.start, bot.stop, bot.restart, bot.delete
# bot.config.update, bot.embed.update, bot.button.update
# user.settings.update, user.role.change
# blacklist.add, blacklist.remove
# webhook.create, webhook.delete
# admin.user.delete, admin.license.generate
```

#### Data Encryption Key Management

```python
# .env file (never committed)
ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET=your-jwt-secret-here
API_KEY_SALT=your-api-key-salt-here

# Key rotation: re-encrypt all fields with new key
# python -m autosecure.tools.rotate_keys --new-key
```

### 3.2 Reliability

#### Circuit Breaker

```python
# Stops calling failing services temporarily
from pybreaker import CircuitBreaker

ms_auth_breaker = CircuitBreaker(
    fail_max=5,           # Open after 5 failures
    reset_timeout=60,     # Try again after 60s
    name="microsoft_auth"
)

hypixel_breaker = CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    name="hypixel_api"
)

@ms_auth_breaker
async def login_microsoft(email: str, password: str) -> MSAuthResult:
    ...
```

#### Retry with Backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
)
async def fetch_hypixel_stats(uuid: str) -> dict:
    ...
```

#### Graceful Shutdown

```python
import signal
import asyncio

async def shutdown(signal, loop):
    """Cleanup on shutdown: stop bots, close DB, drain tasks."""
    logger.info(f"Received {signal.name}, shutting down...")
    
    # Stop all worker bots gracefully
    for bot in state.active_bots.values():
        await bot.close()
    
    # Close DB pool
    await database.close()
    
    # Close Redis
    await redis.close()
    
    # Cancel pending tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    
    loop.stop()
```

#### Idempotency

```python
# All write operations have idempotency keys
# Duplicate requests return the same result, no side effects
@app.post("/api/v1/accounts")
async def create_account(
    idempotency_key: str = Header(...),
    account: AccountCreate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.get(IdempotencyRecord, idempotency_key)
    if existing:
        return JSONResponse(status_code=200, content=existing.result)
    
    result = await account_service.create(account, db)
    
    record = IdempotencyRecord(
        key=idempotency_key,
        result=result.model_dump(),
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(record)
    await db.commit()
    
    return result
```

### 3.3 Observability

#### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer() if DEBUG else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

# Usage
log = structlog.get_logger()
log.info("account.secured", uid=uid, user_id=user_id, method="otp", networth=123456)
# Output: {"event": "account.secured", "uid": "...", "user_id": "...", "method": "otp", "networth": 123456, "timestamp": "2026-07-27T00:00:00Z"}
```

#### Health Check

```python
@app.get("/health")
async def health_check():
    checks = {}
    
    # Database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
    
    # Redis
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    
    # Bot status
    checks["active_bots"] = len(state.active_bots)
    checks["active_quarantines"] = len(state.quarantine_map)
    
    status = "healthy" if all(v == "ok" for k, v in checks.items() if k in ("database", "redis")) else "degraded"
    
    return {"status": status, "checks": checks, "uptime": state.uptime}
```

### 3.4 Rate Limiting

```python
# Per-user rate limiting via Redis
from fastapi import Request, HTTPException

async def rate_limit(request: Request, limit: int = 30, window: int = 60):
    user_id = request.state.user_id
    key = f"ratelimit:{user_id}:{request.url.path}"
    
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return {"X-RateLimit-Limit": limit, "X-RateLimit-Remaining": limit - current}
```

---

## 4. Website / Dashboard

### 4.1 Architecture

The dashboard is a **separate Next.js frontend** that communicates with the
FastAPI backend via REST. This separation enables:

- Independent deploy/scaling — frontend can be served from a CDN, Vercel, or
  nginx static hosting; backend stays on the app server.
- Expandability — multiple frontends can consume the same API (admin dashboard,
  user dashboard, mobile app, public status page) without backend changes.
- Modern DX — React Server Components, file-based routing, TypeScript, etc.
- Clean auth boundary — frontend uses JWT (stored in httpOnly cookie via the
  API login endpoint), backend validates JWT on every request.

```
┌──────────────┐       REST/SSE        ┌──────────────────┐
│  Next.js app  │  ←──────────────────→│  FastAPI backend  │
│  (dashboard)  │   /api/v1/* + /health │  (API + bot + tasks)│
└──────────────┘                       └──────────────────┘
        │                                        │
        │ static export or Vercel                │ PostgreSQL + Redis
        ▼                                        ▼
   CDN / nginx                              104.168.24.47
```

### 4.2 Tech Stack

| Component | Choice | Why |
|---|---|---|
| Framework | Next.js 15 (App Router) | RSC, file-based routing, SSR/SSG, API routes |
| Language | TypeScript | Type safety end-to-end |
| Styling | Tailwind CSS 4 | Utility-first, no runtime, design-system friendly |
| UI components | shadcn/ui + Radix | Accessible, customisable, no vendor lock-in |
| Data fetching | TanStack Query (React Query) | Caching, polling, optimistic updates, SSE integration |
| Charts | Recharts | React-native, composable, clean |
| Tables | TanStack Table | Headless, sort/filter/pagination built-in |
| Auth | JWT in httpOnly cookie | Backend sets cookie on login; frontend just sends requests |
| Icons | Lucide React | Clean, tree-shakeable |
| Notifications | Sonner | Toast notifications |

### 4.3 Project Structure (expandable)

```
autosec/
├── autosecure/          # Python backend (FastAPI)
│   └── ...
├── dashboard/           # Next.js frontend  ← NEW
│   ├── app/             # App Router pages
│   │   ├── (auth)/      # Login, register (public)
│   │   ├── (dashboard)/ # Protected dashboard layout
│   │   │   ├── page.tsx              # Overview
│   │   │   ├── accounts/             # Accounts table + detail
│   │   │   ├── bots/                 # Bot management
│   │   │   ├── licenses/             # License management
│   │   │   ├── emails/               # Email inbox viewer
│   │   │   ├── settings/             # User settings
│   │   │   └── logs/                 # Activity logs
│   │   ├── status/      # Public status page
│   │   └── layout.tsx   # Root layout
│   ├── components/      # Shared UI
│   │   ├── ui/          # shadcn/ui primitives
│   │   ├── charts/      # Chart wrappers
│   │   ├── tables/      # Table primitives
│   │   └── layout/      # Sidebar, navbar, etc.
│   ├── lib/            # API client, hooks, utils
│   │   ├── api.ts       # Axios/fetch wrapper
│   │   ├── hooks/       # TanStack Query hooks
│   │   └── types.ts     # Shared TS types (mirror of Pydantic)
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.ts
```

### 4.4 Expandability — Future Dashboards

The API-first architecture means we can add new frontends without touching the
backend:

| Frontend | Description | Status |
|---|---|---|
| **Admin Dashboard** | Full management interface (current build) | Phase 3 |
| **User Dashboard** | Self-service portal for regular users | Future |
| **Public Status Page** | Uptime, service health, no auth | Future |
| **Mobile App** | React Native, same API | Future |
| **Bot Control Panel** | Per-bot config UI served in Discord via web embed | Future |

Each frontend just needs its own `lib/api.ts` configured to the same backend.

### 4.5 Backend Changes for Next.js

The existing `dashboard/app.py` (Jinja2 routes) will be **removed** and replaced
with:

1. **API-only auth** — `POST /api/v1/auth/login` already returns JWT; the
   frontend stores it in an httpOnly cookie via a Set-Cookie response header.
2. **SSE endpoint** — `GET /api/v1/events` streams real-time events
   (account secured, bot status, license redeemed) for the dashboard to
   consume via `EventSource`.
3. **Static serving** (production) — FastAPI serves the Next.js static export
   from `/` via `StaticFiles`, while `/api/*` and `/health` hit the API.

### 4.6 Dashboard Pages (wireframes)

#### Overview (`/`)
```
┌─────────────────────────────────────────────────────┐
│  AutoSecure Dashboard                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Bots     │ │ Accounts │ │ Active   │ │ Revenue││
│  │ Online   │ │ Secured  │ │ Users    │ │ (LTC)  ││
│  │   12     │ │   1,247  │ │    89    │ │  0.5   ││
│  └──────────┘ └──────────┘ └──────────┘ └────────┘│
│                                                     │
│  ┌──────────────────────┐ ┌───────────────────────┐│
│  │ Accounts Secured     │ │ Active Licenses       ││
│  │ (Last 30 days)       │ │ (by tier)             ││
│  │ [Chart.js line]      │ │ [Chart.js donut]      ││
│  └──────────────────────┘ └───────────────────────┘│
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Recent Activity                              │  │
│  │ 2m ago  Account secured (OTP)    user#1234   │  │
│  │ 5m ago  Bot restarted            user#5678   │  │
│  │ 12m ago License redeemed         user#9012   │  │
│  │ 1h ago  Quarantine released      user#3456   │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### Accounts (`/accounts`)
```
┌─────────────────────────────────────────────────────┐
│  Accounts                          [Export CSV]     │
├─────────────────────────────────────────────────────┤
│  Search: [____________] Filter: [All Users ▼]       │
│                                                     │
│  ┌────┬──────────┬──────────┬────────┬─────────┐   │
│  │ # │ Username │ Email    │ Method │ Networth│   │
│  ├────┼──────────┼──────────┼────────┼─────────┤   │
│  │ 1  │ player1  │ x@y.com │ OTP    │ 12.5B   │   │
│  │ 2  │ player2  │ a@b.com │ REC    │ 8.2B    │   │
│  │ 3  │ player3  │ c@d.com │ OTP    │ 3.1B    │   │
│  └────┴──────────┴──────────┴────────┴─────────┘   │
│  [← Prev] Page 1 of 42 [Next →]                    │
│                                                     │
│  Click row → Detail view:                           │
│  - Credentials (encrypted, reveal on click)         │
│  - Hypixel stats (Skyblock, Bedwars, etc.)          │
│  - Activity timeline                                │
│  - Actions: Delete, Re-secure, View SSID            │
└─────────────────────────────────────────────────────┘
```

#### Bots (`/bots`)
```
┌─────────────────────────────────────────────────────┐
│  Bots                                    [+ New]    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Bot #1 — user#1234                          │   │
│  │ Status: 🟢 Online  │  Uptime: 3d 12h        │   │
│  │ Accounts: 45  │  Config: OTP, Ban Check     │   │
│  │ [Restart] [Stop] [Config] [Logs]            │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Bot #2 — user#5678                          │   │
│  │ Status: 🟡 Quarantine  │  Uptime: 1d 6h     │   │
│  │ Accounts: 12  │  Config: REC, Multiplayer   │   │
│  │ [Restart] [Stop] [Config] [Logs]            │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### Licenses (`/licenses`)
```
┌─────────────────────────────────────────────────────┐
│  Licenses                    [+ Generate] [Import]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Active: 89  │  Expired: 23  │  Trial: 12          │
│                                                     │
│  ┌────────────┬──────────┬─────────┬──────────┐    │
│  │ Key        │ User     │ Expires │ Status   │    │
│  ├────────────┼──────────┼─────────┼──────────┤    │
│  │ XXXX-...   │ user#1   │ 30d     │ Active   │    │
│  │ YYYY-...   │ user#2   │ 7d      │ Warning  │    │
│  │ ZZZZ-...   │ user#3   │ Expired │ Expired  │    │
│  └────────────┴──────────┴─────────┴──────────┘    │
│                                                     │
│  Actions: [Extend] [Revoke] [Transfer] [DM User]   │
└─────────────────────────────────────────────────────┘
```

#### Emails (`/emails`)
```
┌─────────────────────────────────────────────────────┐
│  Email Inbox                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Email: [test@autosecure.me ▼]  [Refresh]          │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ From: noreply@microsoft.com                  │   │
│  │ Subject: Your verification code              │   │
│  │ Time: 2 minutes ago                         │   │
│  │                                              │   │
│  │ Your code is: 312849                        │   │
│  │                                              │   │
│  │ [Copy Code] [Forward] [Delete]              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Real-time: ● Live (auto-refresh via SSE)           │
└─────────────────────────────────────────────────────┘
```

#### Settings (`/settings`)
```
┌─────────────────────────────────────────────────────┐
│  Settings                                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  General                                            │
│  ├─ Domain: [autosecure.me        ]                 │
│  ├─ Default PFP: [URL            ]                  │
│  └─ Trial Duration: [8h          ]                  │
│                                                     │
│  Discord                                             │
│  ├─ Guild ID: [                ]                    │
│  ├─ Role ID: [                 ]                    │
│  ├─ Welcome Channel: [          ]                   │
│  └─ Log Channel: [             ]                    │
│                                                     │
│  Webhooks                                            │
│  ├─ Notifier: [URL              ]                   │
│  └─ [Add New Webhook]                               │
│                                                     │
│  Default Embeds                                      │
│  ├─ [Edit Main Verification Embed]                  │
│  ├─ [Edit OTP Embed]                                │
│  └─ [Edit Error Embeds]                             │
│                                                     │
│  [Save Changes]                                     │
└─────────────────────────────────────────────────────┘
```

#### Logs (`/logs`)
```
┌─────────────────────────────────────────────────────┐
│  Activity Logs                    [Export] [Clear]  │
├─────────────────────────────────────────────────────┤
│  Filter: [All Actions ▼] User: [________]           │
│  Date: [From] to [To]                               │
│                                                     │
│  ┌────┬────────────┬──────────┬──────────┬───────┐ │
│  │ Time │ Action     │ Actor    │ Target   │ Result│ │
│  ├────┼────────────┼──────────┼──────────┼───────┤ │
│  │ 00:01│ acc.secure │ user#1   │ player1  │ ✓     │ │
│  │ 00:02│ bot.restart│ admin    │ user#2   │ ✓     │ │
│  │ 00:03│ lic.redeem │ user#3   │ XXXX-... │ ✗     │ │
│  └────┴────────────┴──────────┴──────────┴───────┘ │
│  [← Prev] Page 1 of 128 [Next →]                   │
└─────────────────────────────────────────────────────┘
```

### 4.7 Frontend Implementation Pattern

```typescript
// dashboard/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export class APIClient {
  private cookies: Record<string, string> = {};

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: "include",
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    if (!res.ok) throw new APIError(res.status, await res.json());
    return res.json();
  }
}

export const api = new APIClient();

// dashboard/app/(dashboard)/accounts/page.tsx
export default async function AccountsPage({ searchParams }) {
  const { accounts, total, page, pages } = await api.request(
    `/api/v1/accounts?page=${searchParams.page ?? 1}`
  );
  return <AccountsTable data={accounts} pagination={{ page, pages, total }} />;
}
```

### 4.8 Real-Time Updates (SSE)

```typescript
// dashboard/lib/hooks/useEvents.ts
export function useEvents() {
  useEffect(() => {
    const es = new EventSource(`${API_BASE}/api/v1/events`);
    es.addEventListener("account.secured", (e) => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Account secured!");
    });
    return () => es.close();
  }, []);
}
```

### 4.9 Auth Flow (JWT in httpOnly cookie)

```typescript
// dashboard/app/(auth)/login/actions.ts
"use server";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function login(formData: FormData) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password: formData.get("password") }),
  });
  if (res.ok) {
    const setCookie = res.headers.get("set-cookie");
    if (setCookie) cookies().set("session", parseCookie(setCookie));
    redirect("/");
  }
}
```

---

## 5. Development Phases

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Working Python project with database, config, and basic infrastructure.

**Deliverables:**
- [x] `pyproject.toml` with all dependencies
- [x] `config.yaml` + `.env` with all settings
- [x] `core/config.py` — Pydantic Settings
- [x] `core/database.py` — SQLAlchemy async engine + session
- [x] `core/redis.py` — Redis connection pool
- [x] `core/state.py` — Global state holder
- [x] `core/logging.py` — structlog setup
- [x] `core/exceptions.py` — Exception hierarchy
- [x] `core/middleware.py` — CORS, error handling, request logging
- [x] `core/deps.py` — FastAPI dependency injection
- [x] `core/app.py` — FastAPI app factory with lifespan
- [x] All SQLAlchemy models (30+ tables)
- [x] All repository classes (12 repos)
- [x] Alembic migration setup + initial migration
- [ ] `utils/` — generate, validators, http client, countries, languages

**Testing:** Unit tests for all models and repositories.

### Phase 2: Services Layer (Weeks 3-5)

**Goal:** All business logic translated and working, no Discord dependency.

**Deliverables:**
- [ ] `services/microsoft/` — All 8 modules (auth, oauth, family, devices, profile, privacy, session, tfa)
- [ ] `services/minecraft/` — All 6 modules (auth, profile, ign, skins, bancheck, multiplayer)
- [ ] `services/hypixel/` — All 7 modules (client, stats, skyblock, bedwars, skywars, duels, resolve)
- [ ] `services/securing/` — All 7 modules (otp, recovery, bulk, zyger, own, after, make_primary)
- [ ] `services/email/` — All 4 modules (smtp_server, validator, code_extractor, watcher)
- [ ] `services/payments/` — All 3 modules (wallet, invoice, checker)
- [ ] `services/cosmetics/` — All 2 modules (lunar, laby)
- [ ] `services/quarantine.py`
- [ ] `services/banning.py`
- [ ] `services/notifications.py`
- [ ] `services/captcha.py`

**Testing:** Unit tests for each service (mock external APIs).

### Phase 3: API + Dashboard (Weeks 6-8)

**Goal:** Full REST API + working Next.js web dashboard.

**Deliverables:**
- [x] `api/auth.py` — JWT login/refresh/logout
- [x] `api/accounts.py` — Full CRUD + stats
- [x] `api/bots.py` — Bot management
- [x] `api/licenses.py` — Redeem, transfer, status
- [x] `api/users.py` — Profile + settings
- [x] `api/emails.py` — Email inbox
- [x] `api/webhooks.py` — Webhook management
- [x] `api/health.py` — Health checks
- [x] `api/admin.py` — Admin endpoints
- [ ] `api/events.py` — SSE endpoint for real-time dashboard updates
- [x] `api/models/` — All Pydantic request/response schemas
- [x] **`dashboard/`** — Next.js 15 frontend project
  - [x] `dashboard/lib/api.ts` — API client wrapper
  - [ ] `dashboard/lib/types.ts` — TypeScript types mirroring Pydantic models
  - [ ] `dashboard/lib/hooks/` — TanStack Query hooks
  - [x] `dashboard/components/` — Shared UI (sidebar, navbar, cards, tables)
  - [x] `dashboard/app/login` — Login page with JWT + cookie auth
  - [x] `dashboard/app/` — Overview page (stats cards, system health)
  - [x] `dashboard/app/accounts` — Accounts table + detail
  - [x] `dashboard/app/bots` — Bot management
  - [x] `dashboard/app/licenses` — License management
  - [x] `dashboard/app/emails` — Email inbox viewer  
  - [x] `dashboard/app/settings` — User settings
  - [x] `dashboard/app/logs` — Activity logs (placeholder)
  - [ ] `dashboard/app/status` — Public status page
- [x] RBAC middleware (owner-only decorator done)
- [ ] Audit logging
- [x] Rate limiting
- [ ] Idempotency support
- [x] Remove old Jinja2 `dashboard/app.py` and `dashboard/auth.py`

**Testing:** API integration tests with test client; frontend E2E with Playwright.

### Phase 4: Discord Bot (Weeks 9-11)

**Goal:** Full Discord bot with all commands, buttons, modals.

**Deliverables:**
- [ ] `bot/controller/client.py` — Main bot startup
- [ ] `bot/controller/events/` — All event handlers
- [ ] `bot/controller/commands/` — All 32 slash commands
- [ ] `bot/controller/buttons/` — All 100+ button handlers
- [ ] `bot/controller/modals/` — All 60+ modal handlers
- [ ] `bot/worker/client.py` — Worker bot factory
- [ ] `bot/worker/query.py` — botnumber-aware queries
- [ ] `bot/worker/commands/` — All 17 worker commands
- [ ] `bot/worker/buttons/` — Worker buttons
- [ ] `bot/worker/modals/` — Worker modals
- [ ] `ui/` — All embed builders, panels, components, cards

**Testing:** Bot interaction tests with mock Discord.

### Phase 5: Background Tasks + Events (Week 12)

**Goal:** All scheduled tasks + webhook event system.

**Deliverables:**
- [ ] `tasks/scheduler.py` — Task scheduler
- [ ] `tasks/license_check.py` — 10s interval
- [ ] `tasks/invoice_check.py` — 60s interval
- [ ] `tasks/leaderboard_update.py` — 5min interval
- [ ] `tasks/quarantine_check.py` — 60s + 24h
- [ ] `tasks/notification_poll.py` — 30s interval
- [ ] `tasks/role_sync.py` — 30min interval
- [ ] `tasks/autoclean.py` — Temp file cleanup
- [ ] `webhooks/dispatcher.py` — Webhook fire system
- [ ] `webhooks/models.py` — Webhook subscription model
- [ ] `webhooks/events.py` — Event definitions

**Testing:** Task execution tests.

### Phase 6: Hardening + Polish (Week 13)

**Goal:** Enterprise-grade quality, security audit, performance.

**Deliverables:**
- [ ] Circuit breakers on all external services
- [ ] Retry with backoff on all HTTP calls
- [ ] Graceful shutdown handlers
- [ ] Encryption at rest for all sensitive fields
- [ ] Full audit trail
- [ ] Rate limiting on all endpoints
- [ ] CSP headers on dashboard
- [ ] CSRF protection on all forms
- [ ] Comprehensive error messages (no stack traces to users)
- [ ] Performance profiling (identify bottlenecks)
- [ ] Load testing (simulate 500+ bots)
- [ ] Security audit (OWASP checklist)
- [ ] Documentation (API docs auto-generated, README, architecture diagram)

---

## 6. Detailed File Mapping

### 6.1 JS → Python File Map

Every JS file maps to exactly one Python file. No ambiguity.

```
JS FILE                                    → PYTHON FILE
─────────────────────────────────────────────────────────
ENTRY POINTS
autosecure.js                              → autosecure/core/app.py
skinServer.js                              → autosecure/services/skinserv.py
ecosystem.config.js                        → DELETED (use systemd)

DATABASE
db/database.py                             → autosecure/core/database.py
db/db.js                                   → autosecure/models/ + alembic/
db/access.py                               → autosecure/db/licenses.py
db/blacklist.py                            → autosecure/db/blacklist.py
db/checkmc.py                              → autosecure/utils/minecraft.py
db/deleteuser.py                           → autosecure/db/users.py
db/destroybots.py                          → autosecure/bot/worker/lifecycle.py
db/exportaccounts.py                       → autosecure/tools/export.py
db/formatAccounts.py                       → autosecure/tools/export.py
db/getbotnumber.py                         → autosecure/bot/worker/query.py
db/getkey.py                               → autosecure/services/hypixel/client.py
db/gettablesarray.py                       → autosecure/db/base.py
db/getuserdata.py                          → autosecure/db/users.py
db/getuserid.py                            → autosecure/bot/worker/query.py
db/insertaccount.py                        → autosecure/db/accounts.py
db/isOwner.py                              → autosecure/core/auth.py
db/securedAccountsDb.py                    → autosecure/models/account.py
db/usersCache.py                           → autosecure/core/state.py
db/change_domain.py                        → autosecure/tools/migrate.py

CONTROLLER BOT
mainbot/controllerbot.py                   → autosecure/bot/controller/client.py
mainbot/handlers/botHandler.js             → autosecure/core/state.py
mainbot/handlers/emailHandler.js           → autosecure/services/email/smtp_server.py
mainbot/handlers/eventHandler.js           → autosecure/bot/controller/events/
mainbot/handlers/handleapi.js              → autosecure/api/ (FastAPI)
mainbot/handlers/handleappealnapi.js       → autosecure/api/admin.py
mainbot/handlers/initializeBots.js         → autosecure/bot/worker/lifecycle.py
mainbot/handlers/quarantinehandler.js      → autosecure/services/quarantine.py
mainbot/handlers/quarantineutils.js        → autosecure/services/quarantine.py
mainbot/handlers/quarantineMap.js          → autosecure/core/state.py
mainbot/handlers/welcomeHandler.js         → autosecure/bot/controller/events/on_member.py
mainbot/handlers/buttons/buttonhandlers.js → autosecure/bot/controller/buttons/

MAINBOT COMMANDS (32 files)
mainbot/commands/users/*.js                → autosecure/bot/controller/commands/*.py

MAINBOT BUTTONS (100+ files)
mainbot/Buttons/**/*.js                    → autosecure/bot/controller/buttons/**/*.py

MAINBOT MODALS (60+ files)
mainbot/modals/**/*.js                     → autosecure/bot/controller/modals/**/*.py

MAINBOT EVENTS
mainbot/events/ready/Initialization.js     → autosecure/bot/controller/events/on_ready.py
mainbot/events/interactionCreate/buttons.js → autosecure/bot/controller/events/on_interaction.py
mainbot/events/interactionCreate/commands.js → autosecure/bot/controller/events/on_interaction.py
mainbot/events/interactionCreate/modals.js → autosecure/bot/controller/events/on_interaction.py
mainbot/events/messageCreate/indianprot.js → autosecure/bot/controller/events/on_message.py

MAINBOT UTILS
mainbot/utils/licensechecker.js            → autosecure/tasks/license_check.py
mainbot/utils/leaderboardupdater.js        → autosecure/tasks/leaderboard_update.py
mainbot/utils/usernotifications.js         → autosecure/services/notifications.py
mainbot/utils/purchasepanel.js             → autosecure/ui/panels.py
mainbot/utils/guidepanel.js                → autosecure/ui/panels.py
mainbot/utils/featurepanel.js              → autosecure/ui/panels.py
mainbot/utils/checkroles.js                → autosecure/tasks/role_sync.py
mainbot/utils/checkToken.js                → autosecure/utils/http.py
mainbot/utils/api.js                       → autosecure/services/hypixel/client.py
mainbot/utils/registerCommands.js          → autosecure/bot/controller/events/on_ready.py
mainbot/utils/getLocalCmds.js              → autosecure/utils/discovery.py
mainbot/utils/getFiles.js                  → autosecure/utils/discovery.py
mainbot/utils/getButtons.js                → autosecure/utils/discovery.py
mainbot/utils/getModals.js                 → autosecure/utils/discovery.py
mainbot/utils/generate.js                  → autosecure/utils/generate.py
mainbot/utils/modalBuilder.js              → autosecure/ui/modals.py
mainbot/utils/kill.js                      → autosecure/core/app.py (shutdown)
mainbot/utils/sleep.py                     → autosecure/utils/sleep.py

MAINBOT PURCHASE
mainbot/utils/purchase/invoice.js          → autosecure/services/payments/invoice.py
mainbot/utils/purchase/invoiceutils.js     → autosecure/services/payments/checker.py
mainbot/utils/purchase/invoicemap.js       → autosecure/core/state.py
mainbot/utils/purchase/purchasethread.js   → autosecure/bot/controller/buttons/buypanel/
mainbot/utils/purchase/validLtcAddress.js  → autosecure/services/payments/wallet.py
mainbot/utils/purchase/getKeyFromMnemonic.js → autosecure/services/payments/wallet.py
mainbot/utils/purchase/getAddressFromMnemonic.js → autosecure/services/payments/wallet.py
mainbot/utils/purchase/combined.js         → autosecure/services/payments/
mainbot/utils/purchase/everythingcombined  → autosecure/services/payments/

MAINBOT EMAILS
mainbot/utils/emails/validEmail.js         → autosecure/utils/validators.py
mainbot/utils/emails/randomColor.js        → autosecure/utils/colors.py
mainbot/utils/emails/modalBuilder.js       → autosecure/ui/modals.py
mainbot/utils/emails/generate.js           → autosecure/utils/generate.py
mainbot/utils/emails/embedWrapper.js       → autosecure/ui/embeds.py
mainbot/utils/emails/emailMsg.js           → autosecure/ui/email_viewer.py

MAINBOT SECURE
mainbot/utils/secure/sendott.js            → DELETED (dead code)
mainbot/utils/secure/login.js              → autosecure/services/microsoft/auth.py
mainbot/utils/secure/getLiveData.js        → autosecure/services/microsoft/_http.py
mainbot/utils/utils/getEmailDescription.js → autosecure/services/email/watcher.py
mainbot/utils/utils/extractCode.js         → autosecure/services/email/code_extractor.py

SHOP SYSTEM
mainbot/shop/db.js                         → autosecure/models/shop.py
mainbot/shop/handler.js                    → autosecure/bot/shop/handler.py
mainbot/shop/runtime.js                    → autosecure/bot/shop/runtime.py
mainbot/shop/commands/buy.js               → autosecure/bot/shop/commands/buy.py

AUTODECURE MODULE
autosecure/autosecure.js                    → autosecure/bot/worker/client.py
autosecure/Handlers/eventHandler.js        → autosecure/bot/worker/events/
autosecure/Handlers/buttons/*.js           → autosecure/bot/worker/buttons/
autosecure/Handlers/bulk/*.js              → autosecure/services/securing/bulk.py
autosecure/Commands/**/*.js                → autosecure/bot/worker/commands/*.py
autosecure/Buttons/**/*.js                 → autosecure/bot/worker/buttons/**/*.py
autosecure/modals/**/*.js                  → autosecure/bot/worker/modals/**/*.py
autosecure/events/**/*.js                  → autosecure/bot/worker/events/

AUTODECURE UTILS
autosecure/utils/modalBuilder.js           → DELETED (duplicate)
autosecure/utils/generate.js               → DELETED (duplicate)
autosecure/utils/visageHandler.js          → DELETED (empty)
autosecure/utils/visage/index.js           → DELETED (empty)
autosecure/utils/settings/listSettings.js  → autosecure/ui/panels.py
autosecure/utils/settings/listConfiguration.js → autosecure/ui/panels.py
autosecure/utils/responses/*.js            → autosecure/ui/defaults.py
autosecure/utils/accounts/*.js             → autosecure/ui/accounts.py
autosecure/utils/embeds/*.js               → autosecure/ui/embeds.py
autosecure/utils/stats/*.js                → autosecure/ui/stats_card.py
autosecure/utils/notifications/*.js        → autosecure/services/notifications.py
autosecure/utils/bot/*.js                  → autosecure/bot/worker/ management
autosecure/utils/process/HttpClient.js     → autosecure/utils/http.py
autosecure/utils/process/helpers.js        → autosecure/utils/ (split)
autosecure/utils/family/*.js               → autosecure/services/microsoft/family.py
autosecure/utils/consents/*.js             → autosecure/services/microsoft/oauth.py
autosecure/utils/devices/*.js              → autosecure/services/microsoft/devices.py
autosecure/utils/changeinfo/*.js           → autosecure/services/microsoft/profile.py
autosecure/utils/minecraft/*.js            → autosecure/services/minecraft/
autosecure/utils/hypixelapi/*.js           → autosecure/services/hypixel/
autosecure/utils/cosmetics/*.js            → autosecure/services/cosmetics/
autosecure/utils/bancheckappeal/*.js       → autosecure/services/banning.py
autosecure/utils/secure/*.js               → autosecure/services/securing/
autosecure/utils/emails/*.js               → autosecure/services/email/
autosecure/utils/imageHandler/*.js         → autosecure/ui/stats_card.py
autosecure/utils/drawhit.js                → autosecure/ui/stats_card.py
autosecure/utils/autocleaner.js            → autosecure/tasks/autoclean.py

STORE
store/emotes.json                          → assets/data/emotes.json
store/cosmetics.json                       → assets/data/cosmetics.json
store/assetsloader.py                      → autosecure/utils/assets.py

CONFIG
config.json                                → config.yaml + .env
launcher_accounts.json                     → DELETED
```

### 6.2 Dead Files to Delete

```
autosecure/utils/visageHandler.js          (empty)
autosecure/utils/visage/index.js           (empty)
autosecure/utils/utils/test.js             (empty function)
mainbot/utils/test2.js                     (test script)
autosecure/utils/testdraw.js               (test script)
autosecure/utils/minecraft/testxbl.js      (test with hardcoded token)
autosecure/utils/lunarapi/src/test.js      (test that auto-executes)
mainbot/utils/secure/sendott.js            (returns null)
autosecure/utils/secure/sendott.js         (returns null)
mainbot/utils/purchase/combined.js         (empty object)
launcher_accounts.json                     (empty)
db/email_reccode.txt                       (JS disguised as txt)
```

---

## 7. Quality Standards

### 7.1 Code Style

```python
# ruff config in pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "SIM", "TCH"]
# E: pycodestyle errors
# F: pyflakes
# I: isort
# N: pep8-naming
# UP: pyupgrade
# B: flake8-bugbear
# A: flake8-builtins
# SIM: flake8-simplify
# TCH: flake8-type-checking

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]
```

### 7.2 File Structure Rules

1. **Max 200 lines per file.** If longer, split.
2. **One class per file** (except small dataclasses in models).
3. **No relative imports.** Always absolute: `from autosecure.services.microsoft import auth`.
4. **No `*` imports.** Always explicit: `from autosecure.utils.generate import generate_uid`.
5. **No mutable module-level state.** Use `state.py` for globals.
6. **No print().** Use `structlog.get_logger()`.
7. **No bare except.** Always catch specific exceptions.

### 7.3 Type Hints

```python
# Every function has type hints
async def get_account_by_uid(uid: str, db: AsyncSession) -> Account | None:
    """Fetch a secured account by its unique ID."""
    ...

# Every class has typed attributes
class AccountCreate(BaseModel):
    uid: str
    user_id: str
    username: str
    email: str | None = None
    recovery_code: str | None = None
    networth: int = 0
    method: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for all API inputs/outputs
class AccountResponse(BaseModel):
    uid: str
    username: str
    method: str
    networth: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 7.4 Docstrings

```python
# Google style docstrings
async def secure_account(
    email: str,
    credentials: str,
    method: SecureMethod,
    user_id: str,
    db: AsyncSession,
) -> Account:
    """Secure a Microsoft account using the specified method.
    
    Args:
        email: The Microsoft account email.
        credentials: Recovery code, OTP, or MSAUTH cookie.
        method: The securing method to use.
        user_id: The Discord user ID requesting the secure.
        db: Database session.
    
    Returns:
        The secured account with credentials.
    
    Raises:
        InvalidCredentials: If the provided credentials are invalid.
        AccountLocked: If the account is locked by Microsoft.
        RateLimited: If too many attempts.
    """
```

### 7.5 Error Handling

```python
# Custom exceptions with HTTP status codes
class AutoSecureError(Exception):
    """Base exception for all AutoSecure errors."""
    status_code: int = 500
    detail: str = "Internal server error"

class InvalidCredentials(AutoSecureError):
    status_code = 401
    detail = "Invalid credentials provided"

class AccountLocked(AutoSecureError):
    status_code = 423
    detail = "Account is locked by Microsoft"

class RateLimited(AutoSecureError):
    status_code = 429
    detail = "Too many requests, please try again later"

class NotFound(AutoSecureError):
    status_code = 404
    detail = "Resource not found"

class Forbidden(AutoSecureError):
    status_code = 403
    detail = "You don't have permission to do this"

# FastAPI exception handler
@app.exception_handler(AutoSecureError)
async def autosecure_error_handler(request: Request, exc: AutoSecureError):
    log.error("error", error=exc.__class__.__name__, detail=exc.detail, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "detail": exc.detail},
    )
```

### 7.6 Testing Standards

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

# tests/test_api/test_accounts.py
@pytest.mark.asyncio
async def test_create_account(client, db):
    response = await client.post("/api/v1/accounts", json={
        "uid": "test123",
        "username": "TestPlayer",
        "email": "test@example.com",
        "method": "otp",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["uid"] == "test123"
    assert data["username"] == "TestPlayer"

@pytest.mark.asyncio
async def test_create_account_duplicate(client, db):
    await client.post("/api/v1/accounts", json={...})
    response = await client.post("/api/v1/accounts", json={...})
    assert response.status_code == 409
```

### 7.7 Documentation Standards

Every module has:
1. Module-level docstring explaining purpose
2. All public functions/classes have docstrings
3. Complex algorithms have inline comments
4. `README.md` in each major directory
5. Auto-generated API docs from FastAPI (OpenAPI/Swagger)

---

## Appendix: Dependency Versions

```toml
[project]
name = "autosecure"
version = "1.0.0"
requires-python = ">=3.12"

[project.dependencies]
# Web
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = ">=0.34.0"}
jinja2 = ">=3.1.0"
python-multipart = ">=0.0.18"
sse-starlette = ">=2.0.0"
itsdangerous = ">=2.2.0"

# Database
sqlalchemy = {extras = ["asyncio"], version = ">=2.0.0"}
asyncpg = ">=0.30.0"
alembic = ">=1.14.0"

# Redis
redis = {extras = ["hiredis"], version = ">=5.0.0"}

# Auth
pyjwt = ">=2.10.0"
passlib = {extras = ["bcrypt"], version = ">=1.7.4"}
cryptography = ">=44.0.0"

# HTTP
httpx = ">=0.28.0"
aiohttp = ">=3.11.0"

# Minecraft
quarry = ">=3.1.0"

# Crypto
mnemonic = ">=0.21"
ecdsa = ">=0.19.0"

# Image
Pillow = ">=11.0.0"

# Email
aiosmtpd = ">=1.4.0"

# Browser
playwright = ">=1.49.0"

# Config
pyyaml = ">=6.0.0"
python-dotenv = ">=1.0.0"
pydantic = ">=2.10.0"
pydantic-settings = ">=2.7.0"

# Logging
structlog = ">=24.0.0"

# Tasks
apscheduler = ">=3.10.0"

# Captcha
twocaptcha = ">=1.0.3"

# Utilities
faker = ">=33.0.0"

# Testing
pytest = ">=8.0.0"
pytest-asyncio = ">=0.25.0"
httpx = ">=0.28.0"

# Dev
ruff = ">=0.8.0"
mypy = ">=1.14.0"
pre-commit = ">=4.0.0"
```
