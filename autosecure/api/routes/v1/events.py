"""Server-Sent Events endpoint for real-time updates."""

from __future__ import annotations

import asyncio
import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from autosecure.core.deps import CurrentUser
from autosecure.core.redis import get_redis

router = APIRouter(tags=["events"])


@router.get("/events")
async def event_stream(user_id: CurrentUser) -> StreamingResponse:
    """Stream real-time events via SSE. Events are published to Redis 'events' channel."""

    async def generate():
        r = get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe("events")

        try:
            # Send initial keepalive
            yield f"data: {json.dumps({'type': 'connected', 'time': time.time()})}\n\n"

            while True:
                message = await asyncio.wait_for(pubsub.get_message(timeout=1.0), timeout=30.0)
                if message and message["type"] == "message":
                    yield f"data: {message['data']}\n\n"
        except asyncio.TimeoutError:
            # Send keepalive
            yield f"data: {json.dumps({'type': 'ping', 'time': time.time()})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe("events")
            await pubsub.close()

    return StreamingResponse(generate(), media_type="text/event-stream")
