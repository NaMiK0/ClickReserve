from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.repositories.booking import BookingRepository
from backend.app.schemas.booking import BookingCreate


class BookingService:

    def __init__(self, session: AsyncSession, redis_client: Redis):
        self.booking_repo = BookingRepository(session)
        self.redis = redis_client

    async def book_seat(self, booking_data: BookingCreate, user_id: int):
        res = await self.redis.set(f"lock:seat:{booking_data.id_seat}", booking_data.id_seat, nx=True, ex=600)
        if res:
            booking_seat = await self.booking_repo.create_booking(booking_data, user_id)
            return booking_seat
        else:
            raise ValueError("This seat is already booked")


