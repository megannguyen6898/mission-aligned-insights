from pydantic import BaseModel
from typing import Dict


class SignedUrlRequest(BaseModel):
    filename: str
    mime: str
    size: int


class SignedUrlResponse(BaseModel):
    url: str
    fields: Dict[str, str]
    upload_id: int
