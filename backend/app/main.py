import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import async_engine, Base
from redis_client import redis_client
from backend.app.tasks.booking import delete_expired_bookings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(delete_expired_bookings())
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)