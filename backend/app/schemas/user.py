
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    organization_name: Optional[str] = None
    mission: Optional[str] = None
    audience: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    organization_size: Optional[str] = None
    key_goals: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    organization_name: Optional[str] = None
    mission: Optional[str] = None
    audience: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    organization_size: Optional[str] = None
    key_goals: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
