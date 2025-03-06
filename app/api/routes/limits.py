# app/api/routes/limits.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.services.redis_service import RedisService

router = APIRouter()


@router.get("")
async def get_rate_limits(request: Request, response: Response):
    """Get current rate limit information for the client"""
    # Get client identifier
    client_ip = request.client.host

    # Initialize Redis service
    redis = RedisService()

    # Get the same key pattern used in middleware
    rate_limit_key = f"ratelimit:{client_ip}"

    # Get current count from Redis
    current_count_raw = await redis.get(rate_limit_key)
    current_count = int(current_count_raw) if current_count_raw else 0

    # Get current hour for reset time (same logic as middleware)
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    reset_time = current_hour + timedelta(hours=1)

    # Calculate time until reset
    seconds_until_reset = int((reset_time - datetime.utcnow()).total_seconds())
    minutes_until_reset = seconds_until_reset // 60
    seconds_remainder = seconds_until_reset % 60

    # Calculate remaining requests
    remaining = max(0, settings.RATE_LIMIT_REQUESTS - current_count)

    # Add rate limit headers (same as middleware)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))

    # Return detailed information
    return {
        "current_usage": current_count,
        "limit": settings.RATE_LIMIT_REQUESTS,
        "remaining": remaining,
        "reset_at": reset_time.isoformat(),
        "reset_in_seconds": seconds_until_reset,
        "reset_in_minutes": minutes_until_reset,
        "reset_in_time": f"{minutes_until_reset}m {seconds_remainder}s",
        "percentage_used": (
                                       current_count / settings.RATE_LIMIT_REQUESTS) * 100 if settings.RATE_LIMIT_REQUESTS > 0 else 0
    }
