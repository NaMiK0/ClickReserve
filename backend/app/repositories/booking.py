from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

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
       query = delete(Booking).where(
           Booking.status == BookingStatus.PENDING,
           Booking.expires_at < datetime.now()
       )
       res = await self.session.execute(query)
       cursor_res = cast(CursorResult, res)
       await self.session.commit()

       return cursor_res.rowcount