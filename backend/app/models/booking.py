from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from backend.app.database import Base
import enum
from datetime import datetime

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"

class Booking(Base):
    __tablename__ = "booking"
    id: Mapped[int] = mapped_column("id", primary_key=True)
    status: Mapped[BookingStatus] = mapped_column("status", default=BookingStatus.PENDING)
    id_seat: Mapped[int] = mapped_column(ForeignKey("seat.id"))
    created_at: Mapped[datetime] = mapped_column("created_at")
    expires_at: Mapped[datetime] = mapped_column("expires_at")