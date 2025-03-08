import json
import logging
from datetime import datetime, timedelta

from fastapi import Request, Response

from app.core.config import settings
from app.services.redis_service import RedisService

# Set up logger
logger = logging.getLogger("rate_limit_middleware")


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to implement rate limiting with detailed logging"""
    # Log the start of middleware execution
    # logger.info(f"Rate limit middleware called for path: {request.url.path}, method: {request.method}")

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
    #     logger.info(f"Normalized path: {normalized_path}")

    # Check if path should be excluded
    is_excluded = (
            normalized_path == "/" or  # Root path
            any(normalized_path.startswith(path) for path in excluded_paths)
    )
    #     logger.info(f"Path excluded from rate limiting: {is_excluded}")

    # Define paths that should be rate limited
    rate_limited_paths = ["/api/v1/combined"]

    # Check if this is a request that should be rate limited
    should_rate_limit = (
            not is_excluded and
            request.method == "POST" and
            normalized_path in rate_limited_paths
    )
    #     logger.info(f"Should rate limit: {should_rate_limit}")

    # Get client IP
    client_ip = request.client.host
    #     logger.info(f"Client IP: {client_ip}")

    # Initialize Redis
    redis = RedisService()

    # Create rate limit key
    rate_limit_key = f"ratelimit:{client_ip}"

    # Get current hour for reset time
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    reset_time = current_hour + timedelta(hours=1)
    ttl = int((reset_time - datetime.utcnow()).total_seconds())

    # Default current count
    current_count = 0

    # Only increment if this request should be rate limited
    if should_rate_limit:
        #         logger.info(f"Incrementing rate limit counter for key: {rate_limit_key}")
        try:
            # Increment counter
            current_count = await redis.increment(rate_limit_key, 1, ttl)
            #             logger.info(f"Counter incremented successfully. New value: {current_count}")

            # If rate limit exceeded
            if current_count > settings.RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for {client_ip}. Count: {current_count}")
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
        except Exception as e:
            logger.error(f"Error incrementing counter: {str(e)}")
    else:
        # For non-rate-limited requests, just get the current count
        try:
            current_count_raw = await redis.get(rate_limit_key)
            current_count = int(current_count_raw) if current_count_raw else 0
        #             logger.info(f"Current count (not incrementing): {current_count}")
        except Exception as e:
            logger.error(f"Error getting counter: {str(e)}")

    # Process the request
    #     logger.info("Processing request")
    response = await call_next(request)
    #     logger.info(f"Request processed. Status code: {response.status_code}")

    # Add rate limit headers to all responses
    remaining = max(0, settings.RATE_LIMIT_REQUESTS - current_count)
    #     logger.info(f"Adding rate limit headers. Remaining: {remaining}")
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))

    return response
