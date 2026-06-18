from datetime import datetime

from pydantic import BaseModel, ConfigDict
from backend.app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    id_seat: int

class BookingRead(BookingCreate):
    id: int
    id_user: int
    status: BookingStatus
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)