# Backend Security Documentation

This document outlines the security features implemented in the Mumbl backend, specifically **Rate Limiting** and **CORS (Cross-Origin Resource Sharing)**.

## Overview

The backend implements two key security measures:

1. **Rate Limiting** - Prevents abuse by limiting requests per client
2. **CORS** - Controls which origins can make requests to the backend

## Rate Limiting

### What is Rate Limiting?

Rate limiting restricts the number of requests a client can make within a specific time window. This protects the backend from:
- Abuse and denial-of-service (DoS) attacks
- Excessive resource consumption
- Intentional or accidental spam

### Configuration

Rate limiting is configured via the environment variable `RATE_LIMIT_PER_MINUTE`:

```bash
# Default: 60 requests per minute per client IP
export RATE_LIMIT_PER_MINUTE=60

# Custom limit (e.g., 10 requests per minute)
export RATE_LIMIT_PER_MINUTE=10

# Run the server
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### How It Works

The `RateLimitMiddleware` class:
- Tracks requests by client IP address
- Maintains a rolling window of timestamps for each client
- Blocks requests when the limit is exceeded within the time window
- Returns HTTP 429 (Too Many Requests) status code
- Includes `Retry-After` header indicating when the client can retry

### Example Response

When a client exceeds the rate limit:

```json
{
  "status": 429,
  "detail": "Rate limit exceeded: 60 requests per minute",
  "headers": {
    "Retry-After": "45"
  }
}
```

The `Retry-After: 45` header tells the client to wait 45 seconds before retrying.

### Implementation Details

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic in-memory rate limiter keyed by client IP.
    """
    def __init__(self, app, max_requests: int, window_seconds: int = 60):
        # Tracks request timestamps per client IP
        self._hits = {}
        # Async lock for thread-safe operations
        self._lock = asyncio.Lock()
```

**Key Features:**
- **Async-safe**: Uses `asyncio.Lock()` for thread-safety in concurrent requests
- **Memory-efficient**: Automatically removes old entries outside the time window
- **IP-based**: Tracks requests by client IP (from `request.client.host`)
- **Configurable**: Time window and max requests are customizable

## CORS (Cross-Origin Resource Sharing)

### What is CORS?

CORS is a security mechanism that controls which domains can make requests to your backend. Without proper CORS configuration, browsers block cross-origin requests for security reasons.

### Configuration

CORS is configured via the environment variable `FRONTEND_ORIGIN`:

```bash
# Development (default)
export FRONTEND_ORIGIN=http://localhost:3000

# Production
export FRONTEND_ORIGIN=https://yourdomain.com

# Run the server
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Current Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Parameters:**
- `allow_origins`: Only requests from this origin are allowed
- `allow_credentials`: Allows cookies and authentication headers
- `allow_methods`: All HTTP methods are allowed (GET, POST, PUT, DELETE, etc.)
- `allow_headers`: All headers are allowed in requests

### CORS Preflight Requests

For complex requests (like file uploads), browsers send an OPTIONS preflight request:

```
OPTIONS /transcribe
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

The server responds with allowed methods and headers:

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

### Browsers Check CORS Headers

Modern browsers enforce CORS by checking response headers:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

If the origin is not in the `Allow-Origin` list, the browser blocks the response.

## Testing

### Run All Security Tests

```bash
# All tests
./venv/bin/python -m pytest tests/ -v

# Rate limit tests only
./venv/bin/python -m pytest tests/test_rate_limit.py -v

# CORS tests only
./venv/bin/python -m pytest tests/test_cors.py -v

# Main API tests
./venv/bin/python -m pytest tests/test_main.py -v
```

### Test Coverage

| Feature | Test File | Test Cases |
|---------|-----------|-----------|
| Rate Limiting | `test_rate_limit.py` | 2 tests |
| CORS | `test_cors.py` | 4 tests |
| Main API | `test_main.py` | 3 tests |
| **Total** | | **9 tests** |

### Example Tests

#### Rate Limiting Test
```python
def test_rate_limit_with_actual_requests():
    """Test rate limiting through actual HTTP requests."""
    # Setup test app with low limit (2 requests)
    # Make 3 requests
    # First 2 succeed (200 OK)
    # 3rd is blocked (429 Too Many Requests)
    assert response.status_code == 429
```

#### CORS Test
```python
def test_cors_allowed_origin():
    """Test that allowed origins receive CORS headers."""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
```

## Security Best Practices

### 1. Production Deployment

Before deploying to production:

```bash
# Update CORS to specific domain
export FRONTEND_ORIGIN=https://yourdomain.com

# Adjust rate limit for expected traffic
export RATE_LIMIT_PER_MINUTE=100

# Consider using a reverse proxy (nginx, CloudFlare) for additional protection
```

### 2. Rate Limiting Considerations

- **Shared Network**: Clients behind NAT/proxy share IP address
  - Solution: If needed, use a reverse proxy that adds `X-Forwarded-For` header
  
- **Legitimate Spikes**: Normal traffic spikes may trigger rate limits
  - Solution: Monitor logs and adjust `RATE_LIMIT_PER_MINUTE` accordingly

- **Distributed Attacks**: Rate limiting per IP doesn't prevent distributed attacks
  - Solution: Use a WAF (Web Application Firewall) or CDN for DDoS protection

### 3. CORS Considerations

- **Never Use Wildcard (`*`) in Production**: 
  - ❌ Bad: `allow_origins=["*"]`
  - ✅ Good: `allow_origins=["https://yourdomain.com"]`

- **Multiple Domains**: For multiple domains:
  ```python
  allow_origins=[
      "https://yourdomain.com",
      "https://www.yourdomain.com",
      "https://app.yourdomain.com"
  ]
  ```

- **Wildcard Subdomains**: Use regex:
  ```python
  allow_origin_regex=r"https://.*\.yourdomain\.com"
  ```

### 4. Combined Security Strategy

For optimal security in production:

```bash
# 1. Restrict CORS to your domain
export FRONTEND_ORIGIN=https://yourdomain.com

# 2. Set reasonable rate limit
export RATE_LIMIT_PER_MINUTE=60

# 3. Run behind reverse proxy (nginx)
# 4. Use HTTPS only
# 5. Consider WAF/CDN (CloudFlare, AWS Shield)
# 6. Monitor logs for suspicious patterns
```

## Monitoring and Debugging

### View Rate Limit Logs

```bash
# Example log entry for rate-limited request
tail -f server.log | grep "429"
```

### Check Current Rate Limits

Monitor the `/health` endpoint to test rate limiting:

```bash
# Rapid requests - will hit rate limit
for i in {1..65}; do
  curl http://localhost:8000/health
  echo "Request $i"
done
```

### Debug CORS Issues

If CORS is failing, check:

1. **Browser Console**: Look for CORS error message
2. **Network Tab**: Inspect response headers
3. **Verify Origin Header**: 
   ```bash
   curl -H "Origin: http://localhost:3000" -i http://localhost:8000/health
   ```
4. **Check Environment Variable**:
   ```bash
   echo $FRONTEND_ORIGIN
   ```

## Related Files

- `main.py` - Main application with middleware setup
- `tests/test_rate_limit.py` - Rate limiting tests
- `tests/test_cors.py` - CORS tests
- `requirements.txt` - Python dependencies
- `SETUP.md` - General setup guide

## Future Enhancements

Potential improvements for future versions:

1. **Distributed Rate Limiting**: Use Redis for rate limiting across multiple instances
2. **Advanced CORS**: Dynamic origin validation based on tenant/user
3. **Request Logging**: Enhanced logging for security audits
4. **API Keys**: Per-application API key rate limiting
5. **Geographic Blocking**: Block requests from specific regions (if needed)
6. **Request Signing**: HMAC-SHA256 request signatures for API clients

## Support

For questions or issues related to security:

1. Review this documentation
2. Check test cases in `tests/test_*.py`
3. Review implementation in `main.py`
4. Open an issue on GitHub: https://github.com/gdash-code/mumbl-backend/issues

---

**Last Updated:** December 7, 2025  
**Feature Branch:** `feature/backend-security`  
**Issue:** Implement Backend Security: Rate Limiting & CORS #1
