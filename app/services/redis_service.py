from upstash_redis import Redis
import json
import zlib
import base64
from typing import Any, Optional, Dict, Union
import time

from app.core.config import settings


class RedisService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
            # Initialize Redis connection
            cls._instance.redis = Redis(
                url=settings.UPSTASH_REDIS_URL,
                token=settings.UPSTASH_REDIS_TOKEN
            )
        return cls._instance

    async def get(self, key: str, decompress: bool = False) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            value = self.redis.get(key)
            if value and decompress:
                # Decompress value
                value = zlib.decompress(base64.b64decode(value))
                value = json.loads(value.decode('utf-8'))
            return value
        except Exception as e:
            print(f"Redis error: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 86400, compress: bool = False) -> bool:
        """Set a value in Redis with optional compression"""
        try:
            if compress and isinstance(value, (dict, list, str)):
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                # Compress value
                value = base64.b64encode(zlib.compress(value.encode('utf-8'))).decode('utf-8')

            return self.redis.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis error: {str(e)}")
            return False

    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Increment a counter in Redis"""
        try:
            # Using synchronous Redis client
            if amount == 1:
                current = self.redis.incr(key)
            else:
                current = self.redis.incrby(key, amount)

            # Set expiration if TTL is provided and this is the first increment
            if ttl and current == amount:
                self.redis.expire(key, ttl)

            return current
        except Exception as e:
            print(f"Redis error: {str(e)}")
            return 0

    async def get_status(self, request_id: str) -> Dict[str, Any]:
        """Get processing status for a request"""
        status_key = f"status:{request_id}"
        status = await self.get(status_key)
        if not status:
            return {"status": "not_found"}
        return status if isinstance(status, dict) else json.loads(status)

    async def set_status(self, request_id: str, status: Dict[str, Any], ttl: int = 7200) -> bool:
        """Set processing status for a request with configurable TTL"""
        status_key = f"status:{request_id}"
        return await self.set(status_key, status, ttl)