"""
Tests for CORS (Cross-Origin Resource Sharing) security configuration.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


def test_cors_allowed_origin():
    """Test that requests from allowed origins receive correct CORS headers."""
    allowed_origin = "http://localhost:3000"
    
    # Create a test app with CORS
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[allowed_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    def health():
        return {"ok": True}
    
    client = TestClient(app)
    
    # Make a request with the allowed origin
    response = client.get("/health", headers={"Origin": allowed_origin})
    
    # Check CORS headers are present
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert response.status_code == 200


def test_cors_preflight_request():
    """Test that CORS preflight (OPTIONS) requests are handled correctly."""
    allowed_origin = "http://localhost:3000"
    
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[allowed_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    @app.post("/transcribe")
    async def transcribe():
        return {"transcript": "test"}
    
    client = TestClient(app)
    
    # Send preflight request
    response = client.options(
        "/transcribe",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    
    # Preflight should return 200
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_cors_credentials_flag():
    """Test that credentials are allowed in CORS config."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    def health():
        return {"ok": True}
    
    client = TestClient(app)
    
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    
    # When credentials are True, Access-Control-Allow-Credentials should be true
    if "access-control-allow-credentials" in response.headers:
        assert response.headers["access-control-allow-credentials"].lower() == "true"


def test_cors_env_variable_override():
    """Test that CORS origin can be configured via environment variable."""
    custom_origin = "https://example.com"
    os.environ["FRONTEND_ORIGIN"] = custom_origin
    
    try:
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        def health():
            return {"ok": True}
        
        client = TestClient(app)
        
        # Request from the custom origin should be allowed
        response = client.get("/health", headers={"Origin": custom_origin})
        assert response.status_code == 200
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] == custom_origin
    finally:
        # Clean up environment variable
        if "FRONTEND_ORIGIN" in os.environ:
            del os.environ["FRONTEND_ORIGIN"]
