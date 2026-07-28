"""Redis connection pool and helpers."""

from __future__ import annotations

from typing import Any

import redis.asyncio as aioredis

from autosecure.core.config import settings

redis_pool: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize the Redis connection pool."""
    global redis_pool
    redis_pool = aioredis.from_url(
        settings.redis.url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None


def get_redis() -> aioredis.Redis:
    """Get the Redis client instance."""
    if redis_pool is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_pool


async def cache_get(key: str) -> Any | None:
    """Get a value from the cache."""
    r = get_redis()
    return await r.get(key)


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    """Set a value in the cache with optional TTL."""
    r = get_redis()
    await r.set(key, value, ex=ttl or settings.redis.cache_ttl)


async def cache_delete(key: str) -> None:
    """Delete a value from the cache."""
    r = get_redis()
    await r.delete(key)


async def rate_limit_check(key: str, limit: int, window: int) -> tuple[bool, int]:
    """Check rate limit. Returns (allowed, remaining)."""
    r = get_redis()
    current = await r.incr(key)
    if current == 1:
        await r.expire(key, window)
    remaining = max(0, limit - current)
    return current <= limit, remaining
