# AutoSecure — Full Website & Security Plan

> Complete blueprint for the AutoSecure platform: public website, user dashboard, admin panel, payment system, and security architecture.

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Security & Permission System](#2-security--permission-system)
3. [Authentication System (Google OAuth)](#3-authentication-system-google-oauth)
4. [Payment System (NowPayments.io)](#4-payment-system-nowpaymentsio)
5. [Full Sitemap](#5-full-sitemap)
6. [Public Website Pages](#6-public-website-pages)
7. [User Dashboard Pages](#7-user-dashboard-pages)
8. [Admin Panel Pages](#8-admin-panel-pages)
9. [Backend API Design](#9-backend-api-design)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Implementation Sprints](#11-implementation-sprints)

---

## 1. Architecture Overview

### Current State

- Backend: FastAPI on port 8000, PostgreSQL, Redis
- Frontend: Next.js 15 on port 3000
- Deployed: Linode VPS `104.168.24.47`
- Auth: Email + password (bcrypt, JWT)
- Roles: Owner vs. everyone (flat)
- Payments: None
- Public pages: Login only

### Target State

- **Auth:** Google OAuth only (no email + password)
- **Roles:** Simple — `admin`, `user`, `banned` (3 roles only)
- **Payments:** NowPayments.io (crypto — BTC, ETH, USDT, etc.)
- **Security:** hCaptcha on login/register, suspicious behavior detection, rate limiting
- **Public site:** Landing, pricing, FAQ, TOS, docs
- **User dashboard:** Scoped to current user's data
- **Admin panel:** Separate layout, system-wide access

### Route Group Separation

```
/                          → Landing page (public)
/login                     → Google OAuth login
/pricing                   → Pricing tiers (public)
/faq                       → FAQ (public)
/tos                       → Terms of Service (public)
/privacy                   → Privacy Policy (public)
/status                    → System status (public)
/docs                      → API docs (public)
/purchase                  → NowPayments checkout flow
/purchase/success          → Payment confirmed
/purchase/cancelled        → Payment cancelled

/dashboard                 → User overview (auth required)
/dashboard/accounts        → My accounts
/dashboard/bots            → My bots
/dashboard/license         → My license status
/dashboard/emails          → Email monitoring
/dashboard/webhooks        → My webhooks
/dashboard/settings        → Profile & preferences
/dashboard/billing         → Purchase history

/admin                     → Admin overview (admin+ required)
/admin/users               → User management
/admin/accounts            → All accounts
/admin/bots                → All bots
/admin/license             → License management
/admin/logs                → Audit logs
/admin/blacklist           → Blacklist management
/admin/config              → Config viewer
```

---

## 2. Security & Permission System

### 2.1 Roles (Simple — 3 Levels Only)

| Role | How Assigned | Privileges |
|------|-------------|------------|
| `user` | Default on Google OAuth signup | Own accounts, bots, licenses, webhooks, emails, settings, billing |
| `admin` | Manually promoted by another admin via `/admin/users` | Everything user can do + manage users, view all data, audit logs, blacklist, config |
| `banned` | Manually banned by admin | Cannot log in, all existing tokens immediately invalid |

There is **no super_admin, no moderator, no support**. Only 3 roles. Admins are fully equal (no "super admin" vs "admin" distinction).

### 2.2 Role Assignment Rules

- **First user:** Gets `user` role (no auto-assign of admin)
- **Admin creation:** Only existing admins can promote users to admin
- **Self-promotion:** Impossible — admin cannot promote themselves
- **Ban:** Admins can ban any user (except other admins)
- **Unban:** Admins can unban any banned user
- **Admin cannot ban admin:** Admin-to-admin ban is blocked
- **Only 1 admin minimum:** System requires at least 1 admin to exist. Prevents locking out all admins

### 2.3 Permissions (Role-Based, Not Granular Flags)

Simple role check — no granular permission flags needed for 3 roles.

```python
# Allowed actions by role:
USER_ACTIONS = {
    "accounts:list", "accounts:create", "accounts:delete",  # own only
    "bots:list", "bots:create", "bots:start", "bots:stop", "bots:restart", "bots:delete", "bots:edit",  # own only
    "licenses:view_own", "licenses:redeem", "licenses:transfer",
    "emails:watch", "emails:read", "emails:unwatch",
    "webhooks:create", "webhooks:delete",
    "users:view_own", "users:edit_own",
    "billing:view_own", "billing:purchase",
}

ADMIN_ACTIONS = USER_ACTIONS | {
    "users:list", "users:view_any", "users:promote", "users:ban", "users:unban", "users:delete",
    "accounts:view_any",
    "bots:view_any",
    "licenses:view_any", "licenses:generate",
    "logs:view",
    "blacklist:manage",
    "config:view",
    "billing:view_any",
}
```

### 2.4 Backend Dependency Injection

```python
# autosecure/core/deps.py

async def require_admin(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: DBSession,
) -> str:
    """Require admin role. Blocks banned users (they can't get tokens)."""
    user = await _get_user(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id


async def require_not_banned(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: DBSession,
) -> str:
    """Verify user is not banned. (Already checked at JWT layer, but double-check.)"""
    user = await _get_user(user_id, db)
    if user and user.is_banned:
        raise HTTPException(status_code=403, detail="Account is banned")
    return user_id


# Updated type aliases
CurrentUser = Annotated[str, Depends(get_current_user_id)]        # Any authenticated user
AdminUser = Annotated[str, Depends(require_admin)]                # Admin only
NotBannedUser = Annotated[str, Depends(require_not_banned)]       # Not banned
```

### 2.5 hCaptcha Integration

**Config (in `.env`):**
```
AUTOSECURE_HCAPTCHA__SITE_KEY="your_site_key_here"
AUTOSECURE_HCAPTCHA__SECRET_KEY="your_secret_key_here"
```

**Config (in `config.yaml`):**
```yaml
hcaptcha:
  site_key: ""              # Set in .env
  secret_key: ""            # Set in .env
  verify_url: "https://api.hcaptcha.com/siteverify"
  enabled: true
```

**Backend verification:**
```python
# autosecure/services/hcaptcha.py

import httpx
from autosecure.core.config import settings

async def verify_hcaptcha(token: str, remote_ip: str) -> bool:
    """Verify hCaptcha response token with hCaptcha API."""
    if not settings.hcaptcha.enabled:
        return True  # Bypass if disabled (for testing)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.hcaptcha.verify_url,
            data={
                "response": token,
                "secret": settings.hcaptcha.secret_key,
                "remoteip": remote_ip,
                "sitekey": settings.hcaptcha.site_key,
            },
            timeout=10,
        )
        result = response.json()
        return result.get("success", False)
```

**Frontend integration:**
```tsx
// components/hcaptcha.tsx
import HCaptcha from "@hcaptcha/react-hcaptcha";

export function CaptchaVerification({ onVerify }: { onVerify: (token: string) => void }) {
  return (
    <HCaptcha
      sitekey={process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY!}
      onVerify={onVerify}
      theme="dark"
    />
  );
}
```

**When hCaptcha is required:**
- Google OAuth callback (first login — verify it's a human)
- NOWPayments invoice creation (prevent bot abuse)
- Any sensitive action that modifies data

**When hCaptcha is NOT required:**
- Viewing data (read-only operations)
- Token refresh
- Public pages

### 2.6 Suspicious Behavior Detection

**Purpose:** Detect and block automated attacks, credential stuffing, and unusual patterns.

**Detection Rules (checked on every request):**

| Rule | Threshold | Action |
|------|-----------|--------|
| Rapid requests | >100 requests in 60s from same IP | Block 15 min |
| Login burst | >5 failed logins in 10 min from same IP | Block IP 30 min |
| Multiple accounts | >3 different Google accounts from same IP in 1 hour | Flag + alert admin |
| Bot-like behavior | Requests with no User-Agent or known bot User-Agent | Block + log |
| Geographic anomaly | Login from new country (compare to last login) | Require hCaptcha |
| Session hijacking | Same JWT used from 2+ different IPs within 5 min | Revoke all tokens |
| Webhook flood | >50 webhook creations in 1 hour from same user | Block user 1 hour |
| License abuse | >10 license redemptions in 1 hour from same user | Flag + alert admin |

**Implementation:**

```python
# autosecure/core/security.py

class SuspiciousBehaviorDetector:
    """Detects and blocks suspicious activity patterns."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_request(self, ip: str, user_id: str | None, path: str) -> dict:
        """Check if request is suspicious. Returns {blocked: bool, reason: str}."""
        checks = [
            self._check_rate_limit(ip),
            self._check_login_burst(ip),
            self._check_bot_user_agent(ip),
            self._check_geo_anomaly(user_id, ip),
            self._check_session_hijack(user_id, ip),
        ]
        for check in checks:
            result = await check
            if result["blocked"]:
                return result
        return {"blocked": False, "reason": ""}

    async def _check_rate_limit(self, ip: str) -> dict:
        """Block if >100 requests in 60s."""
        key = f"security:ratelimit:{ip}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 60)
        if count > 100:
            await self.redis.set(f"security:blocked:{ip}", "rate_limit", ex=900)
            return {"blocked": True, "reason": "Rate limit exceeded"}
        return {"blocked": False}

    async def _check_login_burst(self, ip: str) -> dict:
        """Block IP if >5 login attempts in 10 min."""
        key = f"security:login_attempts:{ip}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 600)
        if count > 5:
            await self.redis.set(f"security:blocked:{ip}", "login_burst", ex=1800)
            return {"blocked": True, "reason": "Too many login attempts"}
        return {"blocked": False}

    async def _check_bot_user_agent(self, ip: str) -> dict:
        """Block known bot user-agents."""
        # Check against list of known bot/crawler user-agents
        # Store in Redis set: security:known_bots
        return {"blocked": False}

    async def _check_geo_anomaly(self, user_id: str | None, ip: str) -> dict:
        """Flag if login from new geographic location."""
        if not user_id:
            return {"blocked": False}
        # Compare IP geolocation to last known location
        # If different country, require hCaptcha on next request
        return {"blocked": False}

    async def _check_session_hijack(self, user_id: str | None, ip: str) -> dict:
        """Revoke tokens if same JWT used from multiple IPs."""
        if not user_id:
            return {"blocked": False}
        key = f"security:session_ip:{user_id}"
        last_ip = await self.redis.get(key)
        if last_ip and last_ip != ip:
            # Different IP — possible session hijacking
            await self.redis.set(key, ip, ex=300)
            # Revoke all tokens for this user
            return {"blocked": False}  # Don't block, but revoke tokens
        await self.redis.set(key, ip, ex=300)
        return {"blocked": False}

    async def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        return await self.redis.exists(f"security:blocked:{ip}")

    async def log_suspicious(self, ip: str, user_id: str | None, reason: str, details: dict):
        """Log suspicious activity for admin review."""
        entry = {
            "ip": ip,
            "user_id": user_id,
            "reason": reason,
            "details": details,
            "timestamp": time.time(),
        }
        await self.redis.lpush("security:suspicious_log", json.dumps(entry))
        await self.redis.ltrim("security:suspicious_log", 0, 999)  # Keep last 1000
```

**Middleware integration:**
```python
# In middleware.py
class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        user_id = _extract_user_id_from_request(request)  # From JWT if present

        # Check if IP is blocked
        if await detector.is_blocked(ip):
            return JSONResponse(status_code=403, content={"error": "Access denied"})

        # Check suspicious behavior
        result = await detector.check_request(ip, user_id, request.url.path)
        if result["blocked"]:
            return JSONResponse(status_code=403, content={"error": result["reason"]})

        response = await call_next(request)
        return response
```

**Admin dashboard for suspicious activity:**
- `GET /api/v1/admin/security/suspicious` — list recent suspicious events
- `POST /api/v1/admin/security/unblock/{ip}` — unblock an IP
- Dashboard shows: blocked IPs, suspicious events count, recent flags

### 2.7 JWT Security

- Access token: 15-minute expiry (short-lived)
- Refresh token: 7-day expiry
- Tokens stored in localStorage (client) + `auth_token` cookie (middleware)
- Refresh rotation: old refresh token revoked in Redis on use
- Token revocation: Redis `revoked:<token>` with TTL = remaining expiry
- **Banned user check at JWT layer:** On every authenticated request, check if user is banned. If banned, revoke token immediately.

### 2.8 API Security

- Per-IP rate limiting: 30 req/60s (existing)
- Per-user rate limiting: 100 req/60s for authenticated endpoints
- CORS: whitelist only `autosecure.me` + `localhost:3000` (dev)
- CSP headers via nginx
- HSTS header via nginx
- Request size limit: 1MB max body
- No secrets in responses (password_hash never returned)
- hCaptcha on sensitive endpoints

### 2.9 Data Protection

- Google OAuth tokens: never stored (only used during callback)
- Database: Connection pool, prepared statements (SQLAlchemy)
- Secrets: Never in git, never in logs, never in API responses
- Encryption key: Fernet for encrypted DB fields

### 2.10 Audit Logging

- Every write operation logged to `audit_logs` table
- Fields: timestamp, actor_id, action, target_type, target_id, details, success, ip_address
- Admin-only access via `GET /api/v1/admin/logs`
- Suspicious events logged separately to Redis (`security:suspicious_log`)

### 2.11 Ban System

- Banned users: `is_banned=True` on User model + `ban_reason`, `banned_at`
- Ban check at JWT decode layer: banned users cannot get new tokens
- Existing tokens for banned users immediately invalid (checked on every authenticated request)
- Admin cannot ban other admins
- System must always have at least 1 admin (prevents lockout)

### 2.12 Anti-Abuse System

#### 2.12.1 Admin Login Protection

- **5-second cooldown per IP** on failed admin login attempts
- After 5 failed attempts from same IP within 10 minutes → block IP for 15 minutes
- Failed login logged with: IP, timestamp, user-agent
- Successful login resets the cooldown counter for that IP
- Applied to: `POST /auth/login` (legacy), `GET /auth/google/callback` (first-time OAuth)
- Implementation: Redis key `auth:cooldown:{ip}` with TTL

#### 2.12.2 Rate Limiting (Global)

- **100 requests per 60 seconds** per IP on all authenticated endpoints
- **30 requests per 60 seconds** per IP on unauthenticated endpoints (health, public status)
- Redis-backed sliding window: `ratelimit:{ip}:{window}`
- Returns `429 Too Many Requests` with `Retry-After` header

#### 2.12.3 DDoS Protection

- Connection rate limit: max 10 new connections/second per IP
- Request body size limit: 1MB max
- Slow client timeout: 30 seconds to send full request
- Implementation: FastAPI middleware checking `Content-Length` and connection count

#### 2.12.4 Request Spam Prevention

- Duplicate request detection: same method + path + body within 2 seconds → reject
- Implementation: Redis key `spam:{ip}:{method}:{body_hash}` with 2s TTL
- Applied to: POST/PUT/DELETE endpoints only (GET is idempotent)

#### 2.12.5 Brute Force Protection

- **Login attempts:** 5 per 10 minutes per IP → block 15 minutes
- **License redeem:** 3 per 10 minutes per user → block 30 minutes
- **Invoice creation:** 5 per hour per user → block 1 hour
- All tracked in Redis with sliding windows

#### 2.12.6 Fake Purchase Protection

- Invoice creation requires valid hCaptcha token
- Invoice status polling rate limit: 10 per minute per user
- IPN callback: verify HMAC-SHA512 signature from NOWPayments
- Duplicate invoice detection: same order_id → reject
- Amount validation: verify paid amount matches expected price (±5% tolerance for crypto)

#### 2.12.7 Bot Detection

- Known bot User-Agents blocked: `bot`, `crawler`, `spider`, `scrapy`, `curl`, `wget`, `python-requests`, `httpclient`, `go-http-client`
- Missing or suspicious User-Agent → flag as suspicious
- Implementation: check in SecurityMiddleware on every request

#### 2.12.8 hCaptcha on Sensitive Endpoints

- `POST /auth/login` (legacy email+password) — requires hCaptcha
- `GET /auth/google` (OAuth initiation) — optional hCaptcha (prevents redirect spam)
- `POST /api/v1/billing/create-invoice` — requires hCaptcha
- `POST /licenses/redeem` — requires hCaptcha
- hCaptcha token verified server-side before processing request
- Frontend: `<HCaptcha>` component on login page, purchase page, redeem page

#### 2.12.9 Geo Anomaly Detection

- Track countries per user: `user:{id}:countries` (Redis set)
- Login from new country → require hCaptcha on next login
- Login from 3+ countries in 24 hours → flag as suspicious
- Implementation: store country from IP geolocation (MaxMind GeoLite2 or similar)

#### 2.12.10 Session Hijacking Detection

- Track IPs per user session: `user:{id}:ips` (Redis sorted set with timestamps)
- Same JWT used from 2+ different IPs within 5 minutes → revoke all tokens for user
- Log as suspicious event: `session_hijacking_suspected`

#### 2.12.11 Suspicious Event Logging

- All detections logged to Redis list: `security:suspicious_log`
- Each event: `{event_type, ip, user_agent, user_id, details, timestamp}`
- Last 1000 events kept in memory, queryable via admin API
- Admin can view and manually unblock IPs

---

## 3. Authentication System (Google OAuth)

### 3.1 Why Google OAuth (Not Email+Password)

- No email sending infrastructure yet
- No SMTP credentials configured
- Google emails are always verified
- Single sign-on: users don't need another password
- hCaptcha integration protects OAuth callback from bots
- Future: can add Discord OAuth later

### 3.2 Google OAuth Flow

```
1. User clicks "Sign in with Google" on /login
2. Frontend redirects to Google OAuth consent screen:
   - Scopes: openid, email, profile
   - Redirect URI: https://autosecure.me/auth/google/callback

3. Google redirects back with authorization code
4. Backend exchanges code for tokens:
   - POST https://oauth2.googleapis.com/token
   - Gets: id_token, access_token, refresh_token

5. Backend validates id_token:
   - Check iss = accounts.google.com
   - Check aud = our client_id
   - Check exp > now
   - Extract: sub (google_id), email, name, picture

6. Backend finds or creates User:
   - Look up by google_id
   - If not found: create new User with google_id, email, name, avatar
   - If first user: assign super_admin role
   - Otherwise: assign user role

7. Backend issues JWT tokens
8. Frontend stores tokens, redirects to /dashboard
```

### 3.3 Google OAuth Config

```yaml
# config.yaml
oauth:
  google:
    client_id: ""        # Set in .env
    client_secret: ""    # Set in .env
    redirect_uri: "https://autosecure.me/auth/google/callback"
    scopes:
      - "openid"
      - "email"
      - "profile"
```

### 3.4 Backend Endpoints

```
GET  /auth/google              → Redirects to Google OAuth consent screen
GET  /auth/google/callback     → Handles callback, creates user, issues JWT
POST /auth/refresh              → Refresh access token
POST /auth/logout               → Invalidate current token
GET  /auth/me                   → Get current user info (from JWT)
```

### 3.5 User Model Changes

```python
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)  # "google_<google_id>"
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, default="")
    avatar_url: Mapped[str] = mapped_column(String, default="")
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    role: Mapped[str] = mapped_column(String, default="user")  # "user", "admin", "banned"
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    banned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    banned_by: Mapped[str | None] = mapped_column(String, nullable=True)  # admin who banned
    email_verified: Mapped[bool] = mapped_column(Boolean, default=True)  # Google emails are verified
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String, nullable=True)  # For geo anomaly detection
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    permissions: Mapped[dict] = mapped_column(JSON, default=dict)  # Reserved for future use
    claiming: Mapped[str] = mapped_column(String, default="none")
    rest_split: Mapped[int] = mapped_column(Integer, default=0)
```

### 3.6 Migration Plan (Existing Users)

Existing users have `user_id` = email address. New users will have `user_id` = `google_<google_id>`.

Strategy:
- Add `google_id` column (nullable initially)
- Add `email`, `name`, `avatar_url` columns
- Add `role`, `is_banned`, `ban_reason`, `banned_at`, `banned_by` columns
- Add `last_login_ip`, `login_count` columns
- Existing users can be linked to Google by adding their google_id later
- Admin can promote existing users to admin via UI
- First person to log in via Google gets `user` role (not admin — admin must be manually promoted)

---

## 4. Payment System (NowPayments.io)

### 4.1 Why NowPayments

- Cryptocurrency payments (BTC, ETH, USDT, SOL, etc.)
- No KYC required for users (crypto-native)
- 300+ supported currencies
- Simple API: create invoice → user pays → webhook confirms
- IPN (Instant Payment Notification) for order confirmation
- Sandbox environment for testing

### 4.2 Integration Flow

```
1. User selects plan on /pricing
2. Clicks "Purchase" → redirected to /purchase
3. User selects payment currency (BTC, ETH, USDT, etc.)
4. Frontend calls POST /api/v1/billing/create-invoice
   - Body: { plan: "monthly" | "yearly" | "lifetime", currency: "btc" }
5. Backend creates NOWPayments invoice:
   - POST https://api.nowpayments.io/v1/invoice
   - Body: { price_amount, price_currency: "usd", pay_currency, order_id, ipn_callback_url }
   - Returns: { id, invoice_url }
6. User redirected to NOWPayments-hosted payment page
7. User pays with crypto
8. NOWPayments sends IPN webhook to our callback URL:
   - POST /api/v1/billing/ipn-callback
   - Body: { order_id, payment_status, pay_address, ... }
9. Backend verifies IPN signature, updates order status
10. If payment confirmed: generate license key, associate with user
11. User redirected to /purchase/success with license key displayed
```

### 4.3 NowPayments Config

```yaml
# config.yaml
billing:
  nowpayments:
    api_key: ""           # Set in .env (NOWPAYMENTS_API_KEY)
    ipn_secret: ""        # Set in .env (NOWPAYMENTS_IPN_SECRET) — for webhook verification
    sandbox: true         # Set to false in production
    callback_url: "https://autosecure.me/api/v1/billing/ipn-callback"
    success_url: "https://autosecure.me/purchase/success"
    cancel_url: "https://autosecure.me/purchase/cancelled"
    base_currency: "usd"  # Prices displayed in USD
    payout_currency: "usdt"  # We receive USDT

  plans:
    monthly:
      price_usd: 9.99
      duration: "30d"
      name: "Monthly"
    yearly:
      price_usd: 79.99
      duration: "365d"
      name: "Yearly"
    lifetime:
      price_usd: 199.99
      duration: "9999d"  # ~27 years
      name: "Lifetime"
```

### 4.4 Backend Endpoints

```
POST /api/v1/billing/create-invoice    → Create NOWPayments invoice
GET  /api/v1/billing/plans             → List available plans and prices
GET  /api/v1/billing/history           → Purchase history for current user
GET  /api/v1/billing/invoice/{id}      → Get invoice details
POST /api/v1/billing/ipn-callback      → NOWPayments webhook (IPN)
GET  /api/v1/billing/verify/{order_id} → Verify payment status (frontend polling)
```

### 4.5 Database Models

```python
class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True)  # Our internal order ID
    plan: Mapped[str] = mapped_column(String)  # "monthly", "yearly", "lifetime"
    price_usd: Mapped[float] = mapped_column(Float)
    currency_paid: Mapped[str] = mapped_column(String, default="")  # "btc", "eth", etc.
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, paid, expired, refunded
    np_invoice_id: Mapped[str | None] = mapped_column(String, nullable=True)  # NOWPayments invoice ID
    license_key: Mapped[str | None] = mapped_column(String, nullable=True)  # Generated license key
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

### 4.6 IPN Webhook Verification

```python
# Verify NOWPayments IPN signature
import hmac
import hashlib

def verify_ipn_signature(body: dict, signature: str, ipn_secret: str) -> bool:
    """Verify NOWPayments IPN callback signature."""
    sorted_body = json.dumps(body, sort_keys=True)
    computed = hmac.new(
        ipn_secret.encode(),
        sorted_body.encode(),
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

### 4.7 License Key Generation

On successful payment:
1. Generate license key: `ASC-{random_hex(4).upper()}-{random_hex(4).upper()}`
2. Create `UsedLicense` record with `user_id` and `expiry` = now + plan duration
3. Link `Purchase.license_key` to the `UsedLicense.license`
4. Return license key to user on success page

---

## 5. Full Sitemap

```
autosecure.me/                              → Landing page
autosecure.me/login                         → Google OAuth login
autosecure.me/pricing                       → Pricing tiers
autosecure.me/faq                           → FAQ
autosecure.me/tos                           → Terms of Service
autosecure.me/privacy                       → Privacy Policy
autosecure.me/status                        → System status
autosecure.me/docs                          → API documentation
autosecure.me/purchase                      → Purchase checkout
autosecure.me/purchase/success              → Payment confirmed
autosecure.me/purchase/cancelled            → Payment cancelled

autosecure.me/auth/google                   → Google OAuth redirect
autosecure.me/auth/google/callback          → OAuth callback

autosecure.me/dashboard                     → User overview
autosecure.me/dashboard/accounts            → My accounts
autosecure.me/dashboard/accounts/[id]       → Account detail
autosecure.me/dashboard/bots                → My bots
autosecure.me/dashboard/bots/[id]           → Bot detail
autosecure.me/dashboard/license             → My license
autosecure.me/dashboard/emails              → Email monitoring
autosecure.me/dashboard/webhooks            → Webhooks
autosecure.me/dashboard/settings            → Profile & settings
autosecure.me/dashboard/billing             → Purchase history

autosecure.me/admin                         → Admin overview
autosecure.me/admin/users                   → User management
autosecure.me/admin/users/[id]              → User detail
autosecure.me/admin/accounts                → All accounts
autosecure.me/admin/bots                    → All bots
autosecure.me/admin/license                 → License management
autosecure.me/admin/logs                    → Audit logs
autosecure.me/admin/blacklist               → Blacklist
autosecure.me/admin/config                  → Config viewer
```

---

## 6. Public Website Pages

### 6.1 Landing Page (`/`)

```
┌─────────────────────────────────────────────┐
│  [Logo]  Home  Pricing  FAQ  Status  [Login]│  ← Navbar
├─────────────────────────────────────────────┤
│                                             │
│  AutoSecure                                │  ← Hero
│  The Ultimate Minecraft Account             │
│  Security Platform                          │
│                                             │
│  [Get Started Free]  [Learn More]           │
│                                             │
├─────────────────────────────────────────────┤
│  🔒 Account Management                      │  ← Features Grid
│  🤖 Bot Automation                          │
│  📧 Email Monitoring                        │
│  ⚡ Real-time Alerts                        │
├─────────────────────────────────────────────┤
│  Monthly    Yearly    Lifetime              │  ← Pricing Preview
│  $9.99/mo   $79.99/yr  $199.99             │
│  [Buy Now]  [Buy Now]  [Buy Now]           │
├─────────────────────────────────────────────┤
│  FAQ Accordion                              │  ← FAQ Preview
├─────────────────────────────────────────────┤
│  [Logo] Links... Socials... © AutoSecure   │  ← Footer
└─────────────────────────────────────────────┘
```

### 6.2 Pricing Page (`/pricing`)

- 3 tier cards: Monthly ($9.99), Yearly ($79.99), Lifetime ($199.99)
- Feature comparison table:
  - Number of accounts
  - Number of bots
  - Email monitoring
  - Webhook support
  - Priority support
  - API access
- "Buy Now" → `/purchase`
- FAQ section at bottom about billing

### 6.3 FAQ Page (`/faq`)

Sections:
- **General:** What is AutoSecure? Is it safe?
- **Accounts:** How do I add an account? What data is stored?
- **Bots:** How do bots work? Can I run multiple?
- **Licenses:** How do I get a license? How long do they last?
- **Billing:** What payment methods? Can I get a refund?
- **Security:** How is my data protected? Do you store passwords?
- **Technical:** API rate limits? Webhook format?

### 6.4 TOS Page (`/tos`)

Standard legal content:
- Acceptance of Terms
- Service Description
- Account Terms
- Payment Terms (NowPayments, no refunds for digital goods)
- License Terms (what the license grants)
- Prohibited Uses
- Intellectual Property
- Limitation of Liability
- Termination
- Dispute Resolution
- Changes to Terms

### 6.5 Privacy Policy (`/privacy`)

- Data Controller: AutoSecure
- Data We Collect: Google profile (name, email, avatar), usage data
- How We Use Data: Service provision, billing, support
- Third Parties: Google (OAuth), NOWPayments (billing), Linode (hosting)
- Data Retention: Account data kept until deletion request
- Your Rights: Access, deletion, portability
- Cookies: auth_token (session), analytics
- Security Measures: encrypted storage, access controls
- Contact: support email

### 6.6 Status Page (`/status`)

Already exists. Enhance with:
- Public nav bar (no auth required)
- Current status: API, Database, Redis
- Uptime percentage (30-day)
- Incident history
- Subscribe to updates

---

## 7. User Dashboard Pages

### 7.1 Overview (`/dashboard`)

```
┌─────────────────────────────────────────────┐
│  [Sidebar]  │  Welcome back, {name}!        │
│             │                               │
│  Dashboard  │  ┌─────────┐ ┌─────────┐     │
│  Accounts   │  │ License │ │ Accounts│     │
│  Bots       │  │ Active  │ │    3    │     │
│  License    │  │ 28 days │ │         │     │
│  Emails     │  └─────────┘ └─────────┘     │
│  Webhooks   │  ┌─────────┐ ┌─────────┐     │
│  Settings   │  │  Bots   │ │ Webhooks│     │
│  Billing    │  │    2    │ │    1    │     │
│             │  │         │ │         │     │
│             │  └─────────┘ └─────────┘     │
│             │                               │
│             │  Quick Actions                │
│             │  [Add Account] [Create Bot]   │
│             │  [Watch Email] [Buy License]  │
│             │                               │
│             │  Recent Activity              │
│             │  • Account added: Steve       │
│             │  • Bot started: Bot #1        │
│             │  • License redeemed           │
└─────────────────────────────────────────────┘
```

### 7.2 My Accounts (`/dashboard/accounts`)

- Table: username, uid, email, networth, created_at
- "Add Account" modal (uid, username, email, recovery_code)
- Delete button per row (confirmation)
- Search by username
- Click row → `/dashboard/accounts/[id]`

### 7.3 Account Detail (`/dashboard/accounts/[id]`)

- Account info card: uid, username, email, method, networth, created_at
- Action bar: Delete (with confirmation)
- No edit (accounts are immutable — only delete + recreate)

### 7.4 My Bots (`/dashboard/bots`)

- Table: bot #, status (running/stopped), created_at
- Start/Stop/Restart/Delete buttons per row
- "Create Bot" modal (Discord bot token)
- Click row → `/dashboard/bots/[id]`

### 7.5 Bot Detail (`/dashboard/bots/[id]`)

- Config editor: domain, activity, dmmode
- Status badge
- Action bar: Start/Stop/Restart/Delete
- Save changes via PUT

### 7.6 My License (`/dashboard/license`)

```
┌─────────────────────────────────────────────┐
│  License Status                             │
│  ┌─────────────────────────────────────┐    │
│  │  Status: Active ✅                  │    │
│  │  Key: ASC-A1B2C3D4-E5F6G7H8        │    │
│  │  Expires: Aug 29, 2026             │    │
│  │  Remaining: 28 days                │    │
│  │  [████████████░░░░░░░░] 70%        │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Redeem License Key                        │
│  [__________] [Redeem]                      │
│                                             │
│  Transfer License                           │
│  To: [__________] [Transfer]                │
│                                             │
│  Don't have a license?                      │
│  [Purchase License →]                       │
└─────────────────────────────────────────────┘
```

### 7.7 Email Monitoring (`/dashboard/emails`)

Already exists. Keep as-is:
- Sidebar: watched addresses, unwatch, add
- Main: email list with expand, auto-refresh

### 7.8 Webhooks (`/dashboard/webhooks`)

Already exists. Keep as-is:
- Table: URL, events, status
- Create/delete

### 7.9 Settings (`/dashboard/settings`)

Tabs:
- **Profile:** Name, email, avatar (from Google, read-only)
- **Password:** Not applicable (Google OAuth)
- **Preferences:** showleaderboard toggle, claiming dropdown, rest_split
- **Security:** Last login time, revoke all sessions

### 7.10 Billing (`/dashboard/billing`)

- Current plan info (if any)
- Purchase history table: date, plan, amount, currency, status
- License key display
- "Buy License" button → `/purchase`

---

## 8. Admin Panel Pages

### 8.1 Admin Overview (`/admin`)

- System stats: total users, accounts, bots, active bots, revenue
- Recent registrations
- Recent purchases
- Active bans
- System health

### 8.2 User Management (`/admin/users`)

- Table: user_id, email, name, role, accounts, bots, created_at, last_login
- Actions: Edit role, Ban/Unban, View detail, Delete
- Search by email/name
- Click row → `/admin/users/[id]`

### 8.3 User Detail (`/admin/users/[id]`)

- Profile: name, email, avatar, role, created_at, last_login
- Ban status (if banned: reason, date)
- Their accounts, bots, licenses, webhooks
- Actions: Change role, Ban, Delete

### 8.4 License Management (`/admin/license`)

- Table: license_key, user_id, status, expires_at
- Generate: count + expiry
- Search/filter

### 8.5 Audit Logs (`/admin/logs`)

Already exists. Keep as-is:
- Filterable table with pagination
- Action, actor, target, status, details

### 8.6 Blacklist (`/admin/blacklist`)

- Table: client_id, reason, added_at
- Add entry, remove entry

### 8.7 Config Viewer (`/admin/config`)

- Read-only view of current config
- Editable fields (selected by owner only)

---

## 9. Backend API Design

### 9.1 Auth Routes (`/auth/*`)

```
GET  /auth/google                → Redirect to Google OAuth
GET  /auth/google/callback       → Handle callback, issue JWT (hCaptcha on first login)
POST /auth/refresh               → Refresh access token
POST /auth/logout                → Invalidate token
GET  /auth/me                    → Current user info
```

### 9.2 User Routes (`/api/v1/users/*`)

```
GET  /api/v1/users/me                     → My profile (name, email, avatar, role)
GET  /api/v1/users/{user_id}              → Any user profile (admin only)
PUT  /api/v1/users/{user_id}/settings     → Update settings (own only)
PUT  /api/v1/users/{user_id}/role         → Change role (admin only, cannot promote to admin)
POST /api/v1/users/{user_id}/ban          → Ban user (admin only, cannot ban other admins)
POST /api/v1/users/{user_id}/unban        → Unban user (admin only)
DELETE /api/v1/users/{user_id}            → Delete user (admin only, cannot delete other admins)
GET  /api/v1/users                        → List all users (admin only)
```

### 9.3 Security Routes (`/api/v1/admin/security/*`)

```
GET  /api/v1/admin/security/suspicious    → List recent suspicious events (admin)
POST /api/v1/admin/security/unblock/{ip}  → Unblock an IP (admin)
GET  /api/v1/admin/security/blocked       → List blocked IPs (admin)
```

### 9.4 Billing Routes (`/api/v1/billing/*`)

```
GET  /api/v1/billing/plans                → List plans and prices
POST /api/v1/billing/create-invoice       → Create NOWPayments invoice (requires hCaptcha)
GET  /api/v1/billing/history              → My purchase history
GET  /api/v1/billing/invoice/{order_id}   → Invoice details
POST /api/v1/billing/ipn-callback         → NOWPayments webhook (IPN)
GET  /api/v1/billing/verify/{order_id}    → Verify payment status
```

### 9.5 Existing Routes (unchanged)

```
GET/POST /api/v1/accounts                 → List/create accounts (own)
DELETE   /api/v1/accounts/{uid}           → Delete account (own)
GET/POST /api/v1/bots                     → List/create bots (own)
GET/PUT/DELETE /api/v1/bots/{id}          → Bot CRUD (own)
POST     /api/v1/bots/{id}/start/stop/restart
GET/POST /api/v1/emails/*                 → Email monitoring
GET/POST/DELETE /api/v1/webhooks/*        → Webhook management
GET      /api/v1/dashboard/stats          → Dashboard stats
GET      /api/v1/admin/*                  → Admin endpoints (admin only)
GET      /api/v1/events                   → SSE endpoint
GET      /api/v1/public/status            → Public health
```

---

## 10. Frontend Architecture

### 10.1 Layout Structure

```
app/
  layout.tsx                    → Root layout (providers, font, dark mode)
  providers.tsx                 → QueryClientProvider, ThemeProvider

  (public)/                     → Public layout (navbar + footer, no sidebar)
    layout.tsx                  → Public nav bar + footer
    page.tsx                    → Landing page
    pricing/page.tsx
    faq/page.tsx
    tos/page.tsx
    privacy/page.tsx
    status/page.tsx
    purchase/page.tsx
    purchase/success/page.tsx
    purchase/cancelled/page.tsx
    docs/page.tsx

  login/page.tsx                → Google OAuth login (no layout wrapper)

  auth/
    google/callback/page.tsx    → OAuth callback handler

  (dashboard)/                  → User dashboard (user sidebar)
    layout.tsx                  → User sidebar + top bar
    page.tsx                    → Overview
    accounts/page.tsx
    accounts/[id]/page.tsx
    bots/page.tsx
    bots/[id]/page.tsx
    license/page.tsx
    emails/page.tsx
    webhooks/page.tsx
    settings/page.tsx
    billing/page.tsx

  (admin)/                      → Admin panel (admin sidebar)
    layout.tsx                  → Admin sidebar + top bar
    page.tsx                    → Admin overview
    users/page.tsx
    users/[id]/page.tsx
    accounts/page.tsx
    bots/page.tsx
    license/page.tsx
    logs/page.tsx
    blacklist/page.tsx
    config/page.tsx
```

### 10.2 Component Architecture

```
components/
  ui/                           → shadcn primitives (existing)
  layout/
    public-nav.tsx              → Public navbar (logo, links, login button)
    public-footer.tsx           → Footer (links, socials, copyright)
    user-sidebar.tsx            → User dashboard sidebar (existing, renamed)
    admin-sidebar.tsx           → Admin sidebar (admin-specific links)
    user-dropdown.tsx           → Avatar dropdown (dashboard, settings, billing, logout)
  features/
    pricing-card.tsx            → Pricing tier card
    faq-accordion.tsx           → FAQ accordion item
    stats-card.tsx              → Stats card (existing)
    empty-state.tsx             → Empty state (existing)
    bot-status-badge.tsx        → Bot status badge (existing)
```

### 10.3 Navigation

**Public visitors:**
```
[Logo]  Home | Pricing | FAQ | Status        [Sign In with Google]
```

**Authenticated users (on /dashboard):**
```
[Logo]  Dashboard | Account | Bots | License | ...    [Avatar ▼]
```
Avatar dropdown: Settings, Billing, Admin (if admin), Sign Out

**Admin users (on /admin):**
```
[Logo]  Admin | Users | Logs | Config | ...    [Avatar ▼]
```

### 10.4 Middleware

```typescript
// middleware.ts

// Public routes (no auth required)
const publicRoutes = ["/", "/login", "/pricing", "/faq", "/tos", "/privacy", "/status", "/docs", "/purchase", "/auth"];

// Auth required for everything else
// Admin routes: /admin/* — check role in frontend (redirect if not admin)

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (publicRoutes.some(r => pathname.startsWith(r))) {
    return NextResponse.next();
  }

  // Allow API, _next, static
  if (pathname.startsWith("/auth") || pathname.startsWith("/api") || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  // Auth check
  const token = request.cookies.get("auth_token")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}
```

---

## 11. Implementation Sprints

### Sprint A: Security Foundation + hCaptcha (Priority: Critical)

**Backend:**
1. Create `autosecure/core/permissions.py` — simple role check (user/admin/banned), no granular flags
2. Update `autosecure/core/deps.py` — `require_admin()`, `require_not_banned()`
3. Update `autosecure/models/user.py` — add `google_id`, `email`, `name`, `avatar_url`, `role`, `is_banned`, `ban_reason`, `banned_at`, `banned_by`, `last_login_ip`, `login_count`, `created_at`, `updated_at`
4. Create `autosecure/models/billing.py` — `Purchase` model
5. Create `autosecure/services/hcaptcha.py` — hCaptcha verification service
6. Create `autosecure/core/security.py` — `SuspiciousBehaviorDetector` class
7. Alembic migration for new columns
8. Update `autosecure/db/users.py` — new methods: `get_by_google_id()`, `get_by_email()`, `update_role()`, `ban_user()`, `unban_user()`
9. Create `autosecure/db/billing.py` — `PurchaseRepo`

**Config:**
- Add hCaptcha config to `config.yaml` and `.env`
- Add security config for suspicious behavior thresholds

**Frontend:**
- Install `@hcaptcha/react-hcaptcha`
- Create `components/hcaptcha.tsx` wrapper
- Update types.ts with new User fields

### Sprint B: Google OAuth (Priority: Critical)

**Backend:**
1. Add `oauth` config section to config.yaml
2. Create `GET /auth/google` — generate state (Redis), redirect to Google
3. Create `GET /auth/google/callback` — exchange code, validate `iss`/`aud`/`nonce`, issue JWT
4. Update `POST /auth/refresh` and `POST /auth/logout`
5. Create `GET /auth/me` — current user info
6. hCaptcha verification on first login (OAuth callback)
7. Log `last_login_at`, `last_login_ip`, `login_count` on each login

**Frontend:**
1. Login page: "Sign in with Google" button (with hCaptcha)
2. `/auth/google/callback` page — handle redirect, store tokens
3. User dropdown with avatar and name

### Sprint C: Anti-Abuse System (Priority: Critical)

**Backend:**
1. Create `autosecure/core/security.py` — `SuspiciousBehaviorDetector` with all detection rules (already exists from Sprint A)
2. Create `SecurityMiddleware` — runs on every request, applies all protections below
3. **Admin login protection:** 5-second cooldown per IP on failed login attempts; 5 failures in 10 min → block 15 min
4. **Global rate limiting:** 100 req/60s (authenticated), 30 req/60s (unauthenticated) — Redis sliding window
5. **DDoS protection:** max 10 new connections/s per IP, 1MB body limit, 30s slow client timeout
6. **Request spam prevention:** same method+path+body within 2s → reject (POST/PUT/DELETE only)
7. **Brute force protection:** 5 logins/10min per IP, 3 license redeems/10min per user, 5 invoices/hour per user
8. **Fake purchase protection:** hCaptcha on invoice creation, HMAC-SHA512 on IPN callback, amount validation (±5%)
9. **Bot detection:** block known bot User-Agents on all requests
10. **hCaptcha on sensitive endpoints:** login, OAuth initiation, invoice creation, license redeem
11. **Geo anomaly:** track countries per user, new country → require hCaptcha, 3+ countries/24h → flag
12. **Session hijacking:** same JWT from 2+ IPs in 5 min → revoke all tokens
13. **Suspicious event logging:** all detections logged to Redis `security:suspicious_log`
14. Create admin API: `GET /api/v1/admin/security/suspicious`, `POST /api/v1/admin/security/unblock/{ip}`, `GET /api/v1/admin/security/blocked`
15. Create `autosecure/services/hcaptcha.py` — hCaptcha verification (already exists from Sprint A)

**Frontend:**
1. Admin security page: blocked IPs, suspicious events, unblock button
2. hCaptcha component on login page (already exists from Sprint A)
3. hCaptcha component on purchase page (Sprint D)

### Sprint D: Payment System (Priority: High)

**Backend:**
1. Add `billing` config section to config.yaml
2. Create `POST /api/v1/billing/create-invoice` — NOWPayments integration (requires hCaptcha)
3. Create `POST /api/v1/billing/ipn-callback` — webhook handler with HMAC-SHA512 verification
4. Create `GET /api/v1/billing/plans`, `GET /api/v1/billing/history`
5. Create `GET /api/v1/billing/verify/{order_id}` — status polling
6. License key generation on successful payment

**Frontend:**
1. `/purchase` page — plan selection, currency selection, NOWPayments redirect (with hCaptcha)
2. `/purchase/success` page — license key displayed, success message
3. `/purchase/cancelled` page — soft cancellation
4. `/dashboard/billing` page — purchase history

### Sprint E: Public Website (Priority: High)

**Frontend:**
1. Public layout (navbar + footer)
2. Landing page (hero, features, pricing preview, FAQ preview)
3. Pricing page (tier cards, comparison table)
4. FAQ page (accordion)
5. TOS page (static content)
6. Privacy page (static content)
7. Update status page (add public nav)

**Backend:**
- Add `GET /api/v1/billing/plans` endpoint for pricing page

### Sprint F: User Dashboard (Priority: High)

**Frontend:**
1. User sidebar (rename existing, update nav items)
2. `/dashboard` overview (scoped stats, license status, activity)
3. `/dashboard/accounts` (scoped to user)
4. `/dashboard/bots` (scoped to user)
5. `/dashboard/license` (status, redeem, transfer, purchase CTA)
6. `/dashboard/settings` (tabs: profile, preferences, security)
7. `/dashboard/billing` (history)

**Backend:**
1. Create `GET /api/v1/dashboard/user-stats` — scoped to current user
2. Create `GET /api/v1/users/me` — user profile with role

### Sprint G: Admin Panel (Priority: Medium)

**Frontend:**
1. Admin sidebar
2. `/admin` overview (system stats, suspicious activity alerts)
3. `/admin/users` (list, search, ban, edit role — cannot ban/promote other admins)
4. `/admin/users/[id]` (detail, actions)
5. `/admin/logs` (existing, move to admin)
6. `/admin/license` (existing, move to admin)
7. `/admin/blacklist` (existing, move to admin)
8. `/admin/security` (blocked IPs, suspicious events, unblock)

**Backend:**
1. Update existing admin routes with `require_admin()` instead of `OwnerUser`
2. Create `POST /api/v1/users/{user_id}/ban` — cannot ban other admins
3. Create `POST /api/v1/users/{user_id}/role` — cannot promote to admin (admin-only action)
4. Create `GET /api/v1/admin/security/*` endpoints

### Sprint H: Security Hardening (Priority: High)

**Backend:**
1. Ban check at JWT decode layer (every authenticated request)
2. Per-user rate limiting (100 req/60s)
3. Audit logging on all write operations
4. Request size limit (1MB)
5. CSP headers in nginx
6. Admin-to-admin ban prevention
7. Minimum 1 admin check (prevent lockout)

**Frontend:**
1. Error boundaries on all pages
2. Loading skeletons (replace "Loading..." text)
3. Consistent empty states
4. Toast notifications on all mutations
5. Mobile responsive design

### Sprint I: Deployment & Polish (Priority: Medium)

**Infrastructure:**
1. nginx reverse proxy (single port 443)
2. Let's Encrypt SSL (certbot)
3. PM2 process manager (auto-restart)
4. GitHub Actions CI/CD
5. CSP + HSTS headers

**Frontend Polish:**
1. SEO: meta tags, Open Graph, structured data
2. Accessibility: aria labels, keyboard navigation
3. Performance: code splitting, image optimization
4. Dark mode (already exists, verify)
5. Mobile responsive
6. Favicon + logo

---

## Appendix: Key Decisions

| Decision | Rationale |
|---|---|
| Google OAuth only | No email infra yet, Google verifies emails natively |
| NowPayments | Crypto-native, no KYC, simple API, IPN webhooks |
| 3 roles only (user/admin/banned) | Simple, no hierarchy complexity, no auto-admin |
| No auto-admin on first user | Security — admin must be manually promoted |
| hCaptcha on sensitive endpoints | Prevents bot abuse on login, invoice creation |
| Suspicious behavior detection | Proactive security — detect and block attacks early |
| Separate layouts | Public / dashboard / admin all have different navs |
| User ID = `google_<id>` | Clean prefix, unique, no collision with existing email-based IDs |
| License on payment | License key generated on payment success, not upfront |
| Ban at JWT layer | Immediate effect, no need to wait for token expiry |
| Admin cannot ban admin | Prevents admin lockout, ensures at least 1 admin always exists |

---

## Appendix: Environment Variables Needed

```bash
# Google OAuth
AUTOSECURE_OAUTH__GOOGLE__CLIENT_ID=...
AUTOSECURE_OAUTH__GOOGLE__CLIENT_SECRET=...

# NowPayments
AUTOSECURE_BILLING__NOWPAYMENTS__API_KEY=...
AUTOSECURE_BILLING__NOWPAYMENTS__IPN_SECRET=...

# hCaptcha (saved in .env — NOT in git)
AUTOSECURE_HCAPTCHA__SITE_KEY=...
AUTOSECURE_HCAPTCHA__SECRET_KEY=...

# Existing (keep)
AUTOSECURE_SECURITY__JWT_SECRET=...
AUTOSECURE_SECURITY__ENCRYPTION_KEY=...
AUTOSECURE_SECURITY__SESSION_SECRET=...
AUTOSECURE_DISCORD__TOKENS=...
```

---

## Appendix: Database Migrations

### Migration: Add Google OAuth + Role + Billing + Security columns

```sql
-- Users table
ALTER TABLE users ADD COLUMN google_id VARCHAR UNIQUE;
ALTER TABLE users ADD COLUMN email VARCHAR UNIQUE;
ALTER TABLE users ADD COLUMN name VARCHAR DEFAULT '';
ALTER TABLE users ADD COLUMN avatar_url VARCHAR DEFAULT '';
ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user';
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN ban_reason VARCHAR;
ALTER TABLE users ADD COLUMN banned_at TIMESTAMP;
ALTER TABLE users ADD COLUMN banned_by VARCHAR;
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;
ALTER TABLE users ADD COLUMN last_login_ip VARCHAR;
ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();

-- Purchases table
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    order_id VARCHAR UNIQUE NOT NULL,
    plan VARCHAR NOT NULL,
    price_usd FLOAT NOT NULL,
    currency_paid VARCHAR DEFAULT '',
    amount_paid FLOAT DEFAULT 0,
    status VARCHAR DEFAULT 'pending',
    np_invoice_id VARCHAR,
    license_key VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP
);
CREATE INDEX idx_purchases_user_id ON purchases(user_id);
```
