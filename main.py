
from fastapi import FastAPI, Header, HTTPException
from RateLimiter import RateLimiter

app = FastAPI(
    title="Intelligent API Rate Limiter",
    description="Week 02 - Big-Tech Engineering Challenge",
    version="0.1.0"
)

# Weekly challenge: 100 requests / 60 seconds
limiter = RateLimiter(limit=100, window=60)


@app.get("/")
def home():
    return {
        "message": "API Rate Limiter is running",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "service": "Rate Limiter API",
        "status": "ok"
    }


@app.get("/limiter-config")
def limiter_config():
    return {
        "limit": limiter.limit,
        "window_seconds": limiter.window,
        "stored_users": limiter.stored_users()
    }


@app.get("/api/data")
def get_data(
    x_demo_user: str = Header(
        default="demo-user",
        alias="X-Demo-User"
    )
):
    # Development-only user identification.
    # Production requires authenticated identity.

    allowed, retry_after = limiter.check_request(x_demo_user)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "Retry-After": str(retry_after)
            }
        )

    return {
        "message": "Request allowed",
        "user": x_demo_user,
        "status": 200
    }
