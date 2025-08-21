from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None


class ActivityResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
