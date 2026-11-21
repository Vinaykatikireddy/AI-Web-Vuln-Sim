from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LabBase(BaseModel):
    name: str
    description: Optional[str] = None
    external_url: Optional[str] = None


class LabAction(BaseModel):
    lab_id: Optional[int] = None


class LabOut(LabBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
