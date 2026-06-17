import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.database import async_engine, Base
from backend.app.redis_client import redis_client
from backend.app.tasks.booking import delete_expired_bookings
from backend.app.models import Booking, Event, Seat  # noqa: F401
from backend.app.routers.booking import router as booking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(delete_expired_bookings())
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(booking_router)