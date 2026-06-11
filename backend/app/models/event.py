from datetime import datetime
from backend.app.database import Base
from sqlalchemy.orm import mapped_column, Mapped


class Event(Base):
    __tablename__ = "event"
    id: Mapped[int] = mapped_column("id", primary_key=True)
    title: Mapped[str] = mapped_column("title")
    description: Mapped[str] = mapped_column("description")
    date: Mapped[datetime] = mapped_column("date")

