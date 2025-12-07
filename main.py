# main.py
"""
Mumbl Backend API - FastAPI application for audio transcription.

Features:
- Audio transcription using faster-whisper (OpenAI Whisper model)
- Rate limiting to prevent abuse (configurable via RATE_LIMIT_PER_MINUTE env var)
- CORS support with origin control (configurable via FRONTEND_ORIGIN env var)
- File upload with size validation (minimum 1KB)

Environment Variables:
- FRONTEND_ORIGIN: Allowed CORS origin (default: http://localhost:3000)
- RATE_LIMIT_PER_MINUTE: Max requests per minute per client IP (default: 60)

Usage:
    export FRONTEND_ORIGIN=http://localhost:3000
    export RATE_LIMIT_PER_MINUTE=60
    uvicorn main:app --host 0.0.0.0 --port 8000
"""
import asyncio
import os
import time
import uuid
from collections import deque

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from settings import settings
from whisper_transcriber import transcribe_audio

app = FastAPI(
    title="Mumbl Backend API",
    description="Audio transcription API powered by OpenAI Whisper",
    version="1.0.0"
)

# CORS Middleware Configuration
# Allows cross-origin requests from the specified frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT_PER_MINUTE = settings.rate_limit_per_minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic in-memory rate limiter keyed by client IP.
    
    Limits the number of requests from each client IP within a time window.
    Returns HTTP 429 (Too Many Requests) when limit is exceeded.
    
    Args:
        app: FastAPI app instance
        max_requests: Maximum requests allowed per window (default: 60)
        window_seconds: Time window in seconds (default: 60)
    
    Attributes:
        _hits: Dictionary mapping client IP to deque of request timestamps
        _lock: Asyncio lock for thread-safe access to _hits
    """

    def __init__(self, app, max_requests: int, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request, call_next):
        """
        Process request and enforce rate limiting.
        
        Args:
            request: Incoming HTTP request
            call_next: Callable to pass request to next middleware
            
        Returns:
            JSONResponse with 429 status if rate limited, otherwise response from next middleware
        """
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
                # Calculate when the oldest request will fall out of the window
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                return JSONResponse(
                    {"detail": f"Rate limit exceeded: {self.max_requests} requests per minute"},
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)

        return await call_next(request)


# Rate Limiting Middleware Configuration
# Enforces rate limiting on all routes
app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
)

UPLOAD_DIR = settings.upload_dir
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _save_upload(file: UploadFile) -> str:
    """
    Save uploaded file to disk and validate size.
    
    Args:
        file: Uploaded file from request
        
    Returns:
        str: Path to saved file
        
    Raises:
        HTTPException: If file is too small (< 1KB)
    """
    file_id = f"{uuid.uuid4()}_{file.filename}"
    dst = os.path.join(UPLOAD_DIR, file_id)

    # rewind in case the stream was peeked
    try:
        file.file.seek(0)
    except Exception:
        pass

    with open(dst, "wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    size = os.path.getsize(dst)
    if size < 1024:
        raise HTTPException(status_code=400, detail=f"Uploaded file too small ({size} bytes)")
    return dst


@app.get("/health")
def health():
    """
    Health check endpoint.
    
    Returns:
        dict: {"ok": True} if service is running
    """
    return {"ok": True}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe audio file using Whisper model.
    
    Args:
        file: Audio file to transcribe (must be > 1KB)
        
    Returns:
        dict: {"transcript": str} - Transcribed text
        
    Raises:
        HTTPException: 
            - 400: File too small
            - 500: Transcription error
    """
    try:
        raw_path = _save_upload(file)
        text = transcribe_audio(raw_path)
        return {"transcript": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
