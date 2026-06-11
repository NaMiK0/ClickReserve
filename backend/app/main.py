from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import async_engine, Base
from redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)