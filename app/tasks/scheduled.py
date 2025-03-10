import asyncio
from datetime import datetime

from app.services.redis_service import RedisService


async def reset_rate_limits():
    """Reset all rate limit counters at the start of each hour"""
    redis = RedisService()
    # Delete all rate limit keys
    keys = redis.redis.keys("ratelimit:*")
    if keys:
        redis.redis.delete(*keys)
    print(f"[{datetime.utcnow()}] Reset all rate limit counters")


async def schedule_tasks():
    """Schedule periodic tasks"""
    while True:
        # Get current time
        now = datetime.utcnow()
        # Calculate seconds until the start of the next hour
        next_hour = now.replace(minute=0, second=0, microsecond=0)
        if next_hour <= now:
            next_hour = next_hour.replace(hour=next_hour.hour + 1)
        seconds_to_wait = (next_hour - now).total_seconds()

        # Wait until the next hour
        await asyncio.sleep(seconds_to_wait)

        # Reset rate limits
        await reset_rate_limits()
