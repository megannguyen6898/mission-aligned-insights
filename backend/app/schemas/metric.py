from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MetricCreate(BaseModel):
    outcome_id: int
    name: str
    value: Optional[float] = None
    recorded_at: Optional[datetime] = None


class MetricResponse(BaseModel):
    id: int
    outcome_id: int
    name: str
    value: Optional[float]
    recorded_at: datetime

    class Config:
        from_attributes = True
