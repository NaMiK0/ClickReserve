from redis import asyncio as aioredis
import asyncio
from config import settings

redis_client = aioredis.from_url(settings.redis_connect, encoding="utf-8")


