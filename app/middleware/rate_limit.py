import json
import logging
from datetime import datetime

from fastapi import Request, Response

from app.core.config import settings
from app.services.redis_service import RedisService

# Set up logger
logger = logging.getLogger("rate_limit_middleware")


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to implement sliding window rate limiting (full hour from each request)"""
    # Define paths that should be excluded from rate limiting
    excluded_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/limits",
        "/api/v1/status",
        "/api/v1/ws"
    ]

    # Normalize path by removing trailing slash
    normalized_path = request.url.path.rstrip('/')

    # Check if path should be excluded
    is_excluded = (
            normalized_path == "/" or  # Root path
            any(normalized_path.startswith(path) for path in excluded_paths)
    )

    # Define paths that should be rate limited
    rate_limited_paths = ["/api/v1/combined"]

    # Check if this is a request that should be rate limited
    should_rate_limit = (
            not is_excluded and
            request.method == "POST" and
            any(normalized_path == path for path in rate_limited_paths)
    )

    # Get client IP
    client_ip = request.client.host

    # Initialize Redis
    redis = RedisService()

    # Create rate limit key
    rate_limit_key = f"ratelimit:{client_ip}"

    # Calculate reset timestamp for headers (1 hour from now)
    reset_timestamp = int((datetime.utcnow().timestamp() + 3600))

    # Default current count
    current_count = 0

    # Only increment if this request should be rate limited
    if should_rate_limit:
        try:
            # Increment counter and set TTL to exactly 1 hour (3600 seconds)
            # This ensures the TTL is refreshed with each request
            current_count = await redis.increment(rate_limit_key, 1, 3600)
            logger.info(f"Counter for {client_ip}: {current_count}/{settings.RATE_LIMIT_REQUESTS}")

            # If rate limit exceeded
            if current_count > settings.RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for {client_ip}. Count: {current_count}")
                response = Response(
                    content=json.dumps({
                        "detail": "Rate limit exceeded. Try again later.",
                        "error_code": "rate_limit_exceeded",
                        "requests_remaining": 0,
                        "reset_at": datetime.fromtimestamp(reset_timestamp).isoformat()
                    }),
                    status_code=429,
                    media_type="application/json"
                )
                return response
        except Exception as e:
            logger.error(f"Error with rate limiting: {str(e)}")
    else:
        # For non-rate-limited requests, just get the current count
        try:
            current_count_raw = await redis.get(rate_limit_key)
            current_count = int(current_count_raw) if current_count_raw else 0
        except Exception as e:
            logger.error(f"Error getting counter: {str(e)}")

    # Process the request
    response = await call_next(request)

    # Add rate limit headers to all responses
    remaining = max(0, settings.RATE_LIMIT_REQUESTS - current_count)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_timestamp)

    return response