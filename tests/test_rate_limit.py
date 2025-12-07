import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from collections import deque
import time

# set a very low limit for tests BEFORE importing app
os.environ["RATE_LIMIT_PER_MINUTE"] = "3"

from fastapi.testclient import TestClient
from main import app, RateLimitMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse

client = TestClient(app)


def test_rate_limit_middleware_directly():
    """Test RateLimitMiddleware functionality directly without TestClient IP issues."""
    middleware = RateLimitMiddleware(None, max_requests=2, window_seconds=60)
    
    # Simulate requests from the same client IP
    async def test():
        # Create mock requests with the same client IP
        mock_requests = []
        for i in range(4):
            mock_request = MagicMock(spec=Request)
            mock_request.client = MagicMock()
            mock_request.client.host = "127.0.0.1"  # Same IP for all requests
            mock_requests.append(mock_request)
        
        # Mock the call_next function
        async def call_next(request):
            return PlainTextResponse("OK")
        
        # First 2 requests should pass
        for i in range(2):
            response = await middleware.dispatch(mock_requests[i], call_next)
            assert response.status_code == 200, f"Request {i+1} should pass"
        
        # 3rd request should be rate limited (429)
        response = await middleware.dispatch(mock_requests[2], call_next)
        assert response.status_code == 429, f"Request 3 should be rate limited"
        
        # Verify Retry-After header exists
        assert "Retry-After" in response.headers
    
    asyncio.run(test())


def test_rate_limit_with_actual_requests():
    """Test rate limiting through actual HTTP requests to the /health endpoint."""
    # Use a custom client that spoofs the same IP
    from fastapi import FastAPI
    from fastapi.testclient import TestClient as FCTestClient
    
    test_app = FastAPI()
    
    # Add CORS middleware (from main.py)
    from fastapi.middleware.cors import CORSMiddleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limit middleware with low limit
    test_app.add_middleware(RateLimitMiddleware, max_requests=2, window_seconds=60)
    
    @test_app.get("/health")
    def health():
        return {"ok": True}
    
    test_client = FCTestClient(test_app)
    
    # Make requests - TestClient should use same IP internally
    responses = []
    for i in range(3):
        resp = test_client.get("/health")
        responses.append(resp)
    
    # First 2 should succeed
    assert responses[0].status_code == 200
    assert responses[1].status_code == 200
    
    # 3rd should be rate limited
    assert responses[2].status_code == 429
    assert "Rate limit exceeded" in responses[2].json()["detail"]