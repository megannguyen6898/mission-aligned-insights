
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DashboardCreate(BaseModel):
    title: str
    topics: List[str]

class DashboardResponse(BaseModel):
    id: int
    title: str
    topics: List[str]
    config_json: Optional[Dict[str, Any]]
    chart_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True
