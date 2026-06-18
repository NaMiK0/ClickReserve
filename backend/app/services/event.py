from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.event import Event
from backend.app.models.seat import Seat
from backend.app.repositories.event import EventRepository
from backend.app.repositories.seat import SeatRepository
from backend.app.schemas.event import EventCreate


class EventService:
    def __init__(self, session: AsyncSession):
        self.event_repo = EventRepository(session)
        self.seat_repo = SeatRepository(session)

    async def get_events(self) -> Sequence[Event]:
        return await self.event_repo.get_events()

    async def create_event_with_seats(self, event_data: EventCreate, count_rows: int, count_cols: int, base_price: Decimal):
        event: Event = await self.event_repo.create_event(event_data)
        event_with_seats: Sequence[Seat] = await self.seat_repo.create_event_seats(event.id, count_rows, count_cols, base_price)

        return event

    async def delete_event(self, event_id: int) -> bool:
        event = await self.event_repo.get_event_by_id(event_id)
        if event is None:
            return False
        await self.event_repo.delete_event(event)
        return True


