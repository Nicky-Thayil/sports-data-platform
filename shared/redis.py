"""
Redis client for the application.
"""

import redis.asyncio as aioredis
from shared.config import get_settings
from functools import lru_cache

@lru_cache()
def get_redis_client() -> aioredis.Redis:
    settings = get_settings()
    return aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )