from datetime import datetime
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.booking import BookingStatus
from backend.app.models.booking import Booking
from backend.app.schemas.booking import BookingCreate


class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_booking(self, booking: BookingCreate) -> Booking:
        booking_seat: Booking = Booking(**booking.model_dump())
        self.session.add(booking_seat)
        await self.session.commit()
        await self.session.refresh(booking_seat)
        return booking_seat

    async def delete_expired_bookings(self):
        res = await self.session.execute(select(Booking).where(Booking.status == BookingStatus.PENDING, Booking.expires_at < datetime.now()))
        deleted_bookings: Sequence[Booking] = res.scalars().all()
        for booking in deleted_bookings:
            await self.session.delete(booking)

        await self.session.commit()





