from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.booking import Booking
from backend.app.schemas.booking import BookingCreate


class BookingRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_booking(self, booking: BookingCreate) -> Booking:
        booking_seat: Booking = Booking(**booking.model_dump())
        self.session.add(booking_seat)
        await self.session.commit()
        await self.session.refresh(booking_seat)
        return booking_seat


