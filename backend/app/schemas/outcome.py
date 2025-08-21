from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OutcomeCreate(BaseModel):
    activity_id: int
    name: str
    description: Optional[str] = None


class OutcomeResponse(BaseModel):
    id: int
    activity_id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
