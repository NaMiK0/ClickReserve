from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict

class SeatStatus(str, Enum):
    FREE = "free"
    LOCKED = "locked"
    BOOKED = "booked"

class SeatCreate(BaseModel):
    row_number: int
    seat_number: int
    price: Decimal

class SeatRead(SeatCreate):
    id: int
    id_event: int
    status: SeatStatus = SeatStatus.FREE
    model_config = ConfigDict(from_attributes=True)