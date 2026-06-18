from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.booking import Booking
    from backend.app.models.event import Event


class Seat(Base):
    __tablename__ = 'seats'
    id: Mapped[int] = mapped_column(primary_key=True)
    row_number: Mapped[int] = mapped_column("row")
    seat_number: Mapped[int] = mapped_column("seat")
    price: Mapped[Decimal] = mapped_column()
    id_event: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))

    event: Mapped["Event"] = relationship(back_populates="seats")
    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="seat", cascade="all, delete-orphan"
    )
