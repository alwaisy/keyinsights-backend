from fastapi import Request, Response
import time
import uuid
from datetime import datetime, timedelta
import json

from app.services.redis_service import RedisService
from app.core.config import settings


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to implement rate limiting"""
    # Skip rate limiting for certain paths
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Get client IP
    client_ip = request.client.host
    redis = RedisService()

    # Create rate limit key
    rate_limit_key = f"ratelimit:{client_ip}"

    # Get current hour for reset time
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    reset_time = current_hour + timedelta(hours=1)
    ttl = int((reset_time - datetime.utcnow()).total_seconds())

    # Check rate limit
    current_count = await redis.increment(rate_limit_key, 1, ttl)

    # If rate limit exceeded
    if current_count > settings.RATE_LIMIT_REQUESTS:
        response = Response(
            content=json.dumps({
                "detail": "Rate limit exceeded. Try again later.",
                "error_code": "rate_limit_exceeded",
                "requests_remaining": 0,
                "reset_at": reset_time.isoformat()
            }),
            status_code=429,
            media_type="application/json"
        )
        return response

    # Process the request
    response = await call_next(request)

    # Add rate limit headers
    remaining = max(0, settings.RATE_LIMIT_REQUESTS - current_count)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))

    return response