from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class SeatCreate(BaseModel):
    row_number: int
    seat_number: int
    price: Decimal

class SeatRead(SeatCreate):
    id: int
    id_event: int
    model_config = ConfigDict(from_attributes=True)