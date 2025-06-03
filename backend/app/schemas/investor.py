
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class InvestorResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    focus_areas: Optional[List[str]]
    funding_type: str
    region: Optional[str]
    sdg_tags: Optional[List[int]]
    ticket_size_min: Optional[float]
    ticket_size_max: Optional[float]
    website_url: Optional[str]
    
    class Config:
        from_attributes = True

class InvestorMatchResponse(BaseModel):
    investor: InvestorResponse
    match_score: float
    filters_applied: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True
