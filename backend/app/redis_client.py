from redis import asyncio as aioredis
from backend.app.config import settings

redis_client = aioredis.from_url(settings.redis_connect, encoding="utf-8")


