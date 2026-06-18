from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventCreate(BaseModel):
    title: str
    description: str
    date: datetime

    @field_validator("date")
    @classmethod
    def strip_timezone(cls, value: datetime) -> datetime:
        # колонка events.date — TIMESTAMP WITHOUT TIME ZONE, поэтому
        # приводим tz-aware дату к наивному UTC
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value


class EventCreateRequest(EventCreate):
    rows: int = Field(gt=0, description="Количество рядов мест")
    cols: int = Field(gt=0, description="Количество мест в ряду")
    base_price: Decimal = Field(gt=0, description="Базовая цена за место")


class EventRead(EventCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
