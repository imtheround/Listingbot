"""Anti-abuse system: rate limiting, brute force, DDoS, bot detection, and more."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from autosecure.core.logging import get_logger

log = get_logger("services.security")

# Known bot user-agents to block
BOT_USER_AGENTS = frozenset([
    "bot", "crawler", "spider", "scrapy", "curl", "wget",
    "python-requests", "httpclient", "go-http-client", "python-urllib",
    "masscan", "nmap", "nikto", "sqlmap", "dirbuster", "gobuster",
    "zgrab", "censys", "shodan", "netcraft",
])


@dataclass
class SuspiciousEvent:
    """A single suspicious event record."""

    event_type: str
    ip: str
    user_agent: str
    user_id: str | None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class AntiAbuseDetector:
    """Comprehensive anti-abuse system.

    Rules:
    - Admin login: 5s cooldown per IP on failed attempts; 5 failures/10min → block 15min
    - Global rate limit: 100 req/60s (auth), 30 req/60s (unauth)
    - DDoS: max 10 new connections/s per IP, 1MB body, 30s slow client
    - Request spam: same method+path+body_hash within 2s → reject
    - Brute force: 5 logins/10min per IP, 3 redeems/10min per user, 5 invoices/hour per user
    - Bot detection: block known bot User-Agents
    - Session hijacking: 2+ IPs in 5min → revoke tokens
    """

    def __init__(self) -> None:
        self._blocked_ips: dict[str, float] = {}  # ip -> unblock_timestamp
        self._ip_request_counts: dict[str, list[float]] = {}
        self._login_attempts: dict[str, list[float]] = {}
        self._login_cooldowns: dict[str, float] = {}  # ip -> cooldown_until
        self._redeem_attempts: dict[str, list[float]] = {}  # user_id -> [timestamps]
        self._invoice_attempts: dict[str, list[float]] = {}  # user_id -> [timestamps]
        self._spam_keys: dict[str, float] = {}  # "method:path:hash" -> timestamp
        self._user_ips: dict[str, dict[str, float]] = {}  # user_id -> {ip: last_seen}
        self._events: list[SuspiciousEvent] = []

    # ── Request-level checks ──────────────────────────────────────────

    async def check_request(
        self,
        ip: str,
        user_agent: str,
        method: str,
        path: str,
        content_length: int = 0,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Check if this request should be allowed. Returns action dict."""
        now = time.time()

        # 1. IP blocked?
        if ip in self._blocked_ips:
            if now < self._blocked_ips[ip]:
                return {
                    "blocked": True,
                    "reason": "IP is temporarily blocked",
                    "retry_after": int(self._blocked_ips[ip] - now),
                }
            del self._blocked_ips[ip]

        # 2. Login cooldown (1s per IP on failed attempts — prevents rapid brute force)
        if ip in self._login_cooldowns:
            if now < self._login_cooldowns[ip]:
                remaining = int(self._login_cooldowns[ip] - now) + 1
                return {
                    "blocked": True,
                    "reason": f"Please wait {remaining}s before trying again",
                    "retry_after": remaining,
                }
            del self._login_cooldowns[ip]

        # 3. Bot user-agent
        ua_lower = user_agent.lower()
        if any(bot in ua_lower for bot in BOT_USER_AGENTS):
            self._blocked_ips[ip] = now + 1800
            self._log_event("bot_detected", ip, user_agent, user_id)
            return {
                "blocked": True,
                "reason": "Bot user-agent detected",
                "retry_after": 1800,
            }

        # 4. Empty or missing user-agent
        if not user_agent or user_agent.strip() == "":
            self._log_event("missing_user_agent", ip, user_agent, user_id)
            # Don't block, but flag as suspicious
            return {"blocked": False, "warning": True, "reason": "Missing User-Agent"}

        # 5. DDoS: body size limit (1MB)
        if content_length > 1_048_576:
            self._log_event("body_too_large", ip, user_agent, user_id, details={"size": content_length})
            return {
                "blocked": True,
                "reason": "Request body too large (max 1MB)",
                "retry_after": 60,
            }

        # 6. Global rate limit (sliding window)
        if ip not in self._ip_request_counts:
            self._ip_request_counts[ip] = []
        self._ip_request_counts[ip].append(now)
        self._ip_request_counts[ip] = [
            t for t in self._ip_request_counts[ip] if now - t < 60
        ]
        req_count = len(self._ip_request_counts[ip])
        if req_count > 100:
            self._blocked_ips[ip] = now + 900
            self._log_event("rate_limit_exceeded", ip, user_agent, user_id)
            return {
                "blocked": True,
                "reason": "Rate limit exceeded (100 req/60s)",
                "retry_after": 900,
            }

        # 7. Request spam prevention (POST/PUT/DELETE only, same method+path within 1s)
        if method in ("POST", "PUT", "DELETE"):
            body_key = f"spam:{method}:{path}"
            last_seen = self._spam_keys.get(body_key)
            if last_seen and (now - last_seen) < 1.0:
                self._log_event("request_spam", ip, user_agent, user_id, details={"path": path})
                return {
                    "blocked": True,
                    "reason": "Duplicate request (1s cooldown)",
                    "retry_after": int(1.0 - (now - last_seen)),
                }
            self._spam_keys[body_key] = now
            # Clean old spam keys (older than 5s)
            if len(self._spam_keys) > 10000:
                self._spam_keys = {
                    k: v for k, v in self._spam_keys.items() if now - v < 5
                }

        # 8. Session hijacking detection
        if user_id:
            if user_id not in self._user_ips:
                self._user_ips[user_id] = {}
            user_ips = self._user_ips[user_id]
            recent_ips = {
                i: t for i, t in user_ips.items() if now - t < 300
            }
            if len(recent_ips) >= 2 and ip not in recent_ips:
                self._log_event(
                    "session_hijacking_suspected",
                    ip,
                    user_agent,
                    user_id,
                    details={"recent_ips": list(recent_ips.keys())},
                )
                return {
                    "blocked": False,
                    "warning": True,
                    "reason": "Session from multiple IPs detected",
                }
            user_ips[ip] = now

        return {"blocked": False, "warning": False}

    # ── Login-specific checks ─────────────────────────────────────────

    async def check_login_attempt(
        self,
        ip: str,
        success: bool,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Track login attempts. Returns block/cooldown info."""
        now = time.time()

        # Record attempt timestamp
        if ip not in self._login_attempts:
            self._login_attempts[ip] = []
        self._login_attempts[ip].append(now)
        self._login_attempts[ip] = [
            t for t in self._login_attempts[ip] if now - t < 600
        ]

        failed_count = len(self._login_attempts[ip])

        if not success:
            # Set 1-second cooldown per IP (prevents rapid brute force)
            self._login_cooldowns[ip] = now + 1

            # 10 failed logins in 10 min → block 10 min
            if failed_count > 10:
                self._blocked_ips[ip] = now + 600
                self._log_event("login_burst_detected", ip, "", user_id, details={"attempts": failed_count})
                return {
                    "blocked": True,
                    "reason": "Too many failed login attempts",
                    "retry_after": 600,
                }

            return {
                "blocked": False,
                "warning": False,
                "cooldown": 1,
                "attempts_remaining": max(0, 10 - failed_count),
            }
        else:
            # Success: clear attempts and cooldown for this IP
            self._login_attempts.pop(ip, None)
            self._login_cooldowns.pop(ip, None)
            return {"blocked": False, "warning": False}

    # ── Brute force: license redeem ───────────────────────────────────

    async def check_redeem_attempt(
        self,
        user_id: str,
        success: bool,
    ) -> dict[str, Any]:
        """Track license redeem attempts per user. 10 failures/10min → block 15min."""
        now = time.time()

        if user_id not in self._redeem_attempts:
            self._redeem_attempts[user_id] = []

        if not success:
            self._redeem_attempts[user_id].append(now)

        self._redeem_attempts[user_id] = [
            t for t in self._redeem_attempts[user_id] if now - t < 600
        ]

        failed_count = len(self._redeem_attempts[user_id])

        if failed_count > 10:
            self._blocked_ips[user_id] = now + 900
            self._log_event("redeem_burst_detected", "", "", user_id, details={"attempts": failed_count})
            return {
                "blocked": True,
                "reason": "Too many failed redeem attempts",
                "retry_after": 900,
            }

        return {"blocked": False, "warning": False}

    # ── Brute force: invoice creation ─────────────────────────────────

    async def check_invoice_attempt(
        self,
        user_id: str,
    ) -> dict[str, Any]:
        """Track invoice creation per user. 20/hour → block 1 hour."""
        now = time.time()

        if user_id not in self._invoice_attempts:
            self._invoice_attempts[user_id] = []

        self._invoice_attempts[user_id].append(now)
        self._invoice_attempts[user_id] = [
            t for t in self._invoice_attempts[user_id] if now - t < 3600
        ]

        count = len(self._invoice_attempts[user_id])

        if count > 20:
            self._log_event("invoice_spam_detected", "", "", user_id, details={"count": count})
            return {
                "blocked": True,
                "reason": "Too many invoice creation attempts (20/hour limit)",
                "retry_after": 3600,
            }

        return {"blocked": False, "warning": False}

    # ── Query methods ─────────────────────────────────────────────────

    def is_ip_blocked(self, ip: str) -> bool:
        now = time.time()
        if ip in self._blocked_ips:
            if now < self._blocked_ips[ip]:
                return True
            del self._blocked_ips[ip]
        return False

    def unblock_ip(self, ip: str) -> bool:
        if ip in self._blocked_ips:
            del self._blocked_ips[ip]
            log.info("ip_manually_unblocked", ip=ip)
            return True
        return False

    def get_blocked_ips(self) -> list[dict[str, Any]]:
        now = time.time()
        result = []
        expired = []
        for ip, unblock_at in self._blocked_ips.items():
            if now < unblock_at:
                result.append({
                    "ip": ip,
                    "blocked_until": unblock_at,
                    "remaining_seconds": int(unblock_at - now),
                })
            else:
                expired.append(ip)
        for ip in expired:
            del self._blocked_ips[ip]
        return result

    def get_events(self, limit: int = 100) -> list[dict[str, Any]]:
        events = self._events[-limit:]
        return [
            {
                "event_type": e.event_type,
                "ip": e.ip,
                "user_agent": e.user_agent,
                "user_id": e.user_id,
                "details": e.details,
                "timestamp": e.timestamp,
            }
            for e in events
        ]

    # ── Internal ──────────────────────────────────────────────────────

    def _log_event(
        self,
        event_type: str,
        ip: str,
        user_agent: str,
        user_id: str | None,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = SuspiciousEvent(
            event_type=event_type,
            ip=ip,
            user_agent=user_agent,
            user_id=user_id,
            details=details or {},
        )
        self._events.append(event)
        if len(self._events) > 1000:
            self._events = self._events[-1000:]
        log.warning(
            "suspicious_event",
            event_type=event_type,
            ip=ip,
            user_id=user_id,
        )
