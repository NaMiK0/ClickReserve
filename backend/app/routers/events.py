from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.routers.dependencies import get_current_admin, get_session
from backend.app.schemas.event import EventCreate, EventCreateRequest, EventRead
from backend.app.services.event import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=Sequence[EventRead])
async def list_events(session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    return await service.get_events()


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_event(
    payload: EventCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    service = EventService(session)
    event_data = EventCreate(
        title=payload.title,
        description=payload.description,
        date=payload.date,
    )
    event = await service.create_event_with_seats(
        event_data,
        count_rows=payload.rows,
        count_cols=payload.cols,
        base_price=payload.base_price,
    )
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def delete_event(
    event_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = EventService(session)
    deleted = await service.delete_event(event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return None
