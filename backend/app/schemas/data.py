
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DataUploadRequest(BaseModel):
    file_name: str
    source_type: str

class DataUploadResponse(BaseModel):
    id: int
    file_name: Optional[str]
    source_type: str
    status: str
    row_count: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
