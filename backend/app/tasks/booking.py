import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import async_engine
from backend.app.repositories.booking import BookingRepository

# нужен для того, чтобы видеть работу воркера в докере
logger = logging.getLogger(__name__)

async def delete_expired_bookings_worker():
    logger.info("Background booking cleanup worker started.")
    while True:
        try:
            async with AsyncSession(async_engine) as session:
                booking_repo = BookingRepository(session)
                count = await booking_repo.delete_expired_bookings()
                if count > 0:
                    logger.info(f"Successfully cleaned up {count} expired PENDING bookings.")
        except Exception as e:
            logger.error(f"Error in booking cleanup worker: {e}")

        await asyncio.sleep(60)