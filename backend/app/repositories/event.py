from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.event import Event
from backend.app.schemas.event import EventCreate


class EventRepository:
    def __init__(self, async_session: AsyncSession):
        self.session = async_session

    async def create_event(self, event_data: EventCreate) -> Event:
        event = Event(**event_data.model_dump())
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)

        return event

    async def get_events(self):
        result = await self.session.execute(select(Event))
        events = result.scalars().all()

        return events

    async def get_event_by_id(self, event_id: int) -> Event | None:
        result = await self.session.execute(select(Event).where(Event.id == event_id))
        return result.scalars().first()

    async def delete_event(self, event: Event) -> None:
        await self.session.delete(event)
        await self.session.commit()
