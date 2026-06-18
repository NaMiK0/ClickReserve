from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.booking import Booking


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    bookings: Mapped[List["Booking"]] = relationship(back_populates="user")
