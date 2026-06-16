import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import async_engine
from backend.app.repositories.booking import BookingRepository


async def delete_expired_bookings():
    while True:
        async with AsyncSession(async_engine) as session:
            booking_repo = BookingRepository(session)
            await booking_repo.delete_expired_bookings()
            await asyncio.sleep(60)