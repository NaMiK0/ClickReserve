import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.redis_client import redis_client
from backend.app.tasks.booking import delete_expired_bookings_worker, logger
from backend.app.models import Booking, Event, Seat  # noqa: F401
from backend.app.routers.booking import router as booking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(delete_expired_bookings_worker())
    yield
    logger.info("Stopping background tasks...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Background booking cleanup worker stopped gracefully.")

    await redis_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(booking_router)