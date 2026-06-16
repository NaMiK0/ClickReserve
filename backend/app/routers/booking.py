from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.redis_client import redis_client
from backend.app.database import async_engine
from backend.app.schemas.booking import BookingCreate
from backend.app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])

async def get_db():
    async with AsyncSession(async_engine) as session:
        yield session

async def get_redis():
    yield redis_client

@router.post("")
async def booking_seat(
        booking_data: BookingCreate,
        session: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
):
    try:
        booking_service = BookingService(session, redis)
        booking = await booking_service.book_seat(booking_data)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))