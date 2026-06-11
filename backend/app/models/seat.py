from decimal import Decimal

from sqlalchemy import ForeignKey

from backend.app.database import Base
from sqlalchemy.orm import mapped_column, Mapped


class Seat(Base):
    __tablename__ = 'seat'
    id: Mapped[int] = mapped_column("id", primary_key=True)
    row_number: Mapped[int] = mapped_column("row")
    seat_number: Mapped[int] = mapped_column("seat")
    price: Mapped[Decimal] = mapped_column("price")
    id_event: Mapped[int] = mapped_column(ForeignKey("event.id"))