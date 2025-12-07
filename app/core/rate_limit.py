# app/core/rate_limit.py
import asyncio
import time
from collections import deque

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic in-memory rate limiter keyed by client IP.
    """

    def __init__(self, app, max_requests: int, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        async with self._lock:
            timestamps = self._hits.get(client_ip)
            if timestamps is None:
                timestamps = deque()
                self._hits[client_ip] = timestamps

            # Drop entries outside the current window
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                return JSONResponse(
                    {"detail": f"Rate limit exceeded: {self.max_requests} requests per minute"},
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)

        return await call_next(request)
