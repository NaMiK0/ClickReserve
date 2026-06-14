from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.functions import func

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
    id_seat: Mapped[int] = mapped_column(ForeignKey("seat.id"))
    status: Mapped[BookingStatus] = mapped_column("status", default=BookingStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column("created_at", server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column("expires_at", server_default=text("now() + interval '10 minutes'"))