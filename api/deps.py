"""
Dependency injection for FastAPI
"""
import redis.asyncio as redis
from config.settings import settings


async def get_redis_client():
    """Get Redis client for job status and caching"""
    return redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis_result_backend():
    """Get Redis client for Celery result backend"""
    return redis.from_url(settings.redis_result_backend, decode_responses=True)
