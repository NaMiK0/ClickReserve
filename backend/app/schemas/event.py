from datetime import datetime
from pydantic import BaseModel, ConfigDict

class EventCreate(BaseModel):
    title: str
    description: str
    date: datetime

class EventRead(EventCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)