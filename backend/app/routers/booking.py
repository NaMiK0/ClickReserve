from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Booking, Seat
from backend.app.redis_client import redis_client
from backend.app.database import async_engine
from backend.app.schemas.booking import BookingCreate, BookingRead
from backend.app.schemas.seat import SeatRead
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

@router.get("", response_model=Sequence[BookingRead])
async def get_bookings(session: AsyncSession = Depends(get_db)) -> Sequence[Booking]:
    res = await session.execute(select(Booking))
    bookings: Sequence[Booking] = res.scalars().all()
    return bookings

@router.get("/events/{id_event}", response_model=Sequence[BookingRead])
async def get_bookings_by_event(id_event: int, session: AsyncSession = Depends(get_db)) -> Sequence[BookingRead]:
    res = await session.execute(select(Booking).join(Seat).where(Seat.id_event == id_event))
    bookings: Sequence[BookingRead] = res.scalars().all()
    return bookings

@router.get("/events/{id_event}/seats", response_model=Sequence[SeatRead])
async def get_seats_by_event(
        id_event: int,
        session: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
) -> Sequence[SeatRead]:
    res = await session.execute(select(Seat).where(Seat.id_event == id_event))
    seats = res.scalars().all()

    if not seats:
        return []

    booked_query = await session.execute(
        select(Booking.id_seat)
        .join(Seat)
        .where(Seat.id_event == id_event)
    )
    booked_seat_ids = set(booked_query.scalars().all())

    keys_of_seats = [f"lock:seat:{seat.id}" for seat in seats]
    lock_seats_for_redis = await redis.mget(keys_of_seats)

    final_seats = []
    for index, seat in enumerate(seats):
        if seat.id in booked_seat_ids:
            current_status = "booked"
        elif lock_seats_for_redis[index] is not None:
            current_status = "locked"
        else:
            current_status = "free"

        final_seats.append(
            SeatRead(
                id=seat.id,
                id_event=seat.id_event,
                row_number=seat.row_number,
                seat_number=seat.seat_number,
                price=seat.price,
                status=current_status
            )
        )

    return final_seats


@router.delete("/events/{id_event}/seats/{id_seat}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seat(
        id_event: int,
        id_seat: int,
        session: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
):

    res = await session.execute(
        select(Booking).where(Booking.id_seat == id_seat)
    )
    booking = res.scalars().first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking for this seat not found"
        )

    await session.delete(booking)
    await redis.delete(f"lock:seat:{id_seat}")
    await session.commit()

    return None
