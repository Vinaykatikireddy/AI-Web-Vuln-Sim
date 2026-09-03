from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class ScanBase(BaseModel):
    lab_id: int
    attack_type: str


class ScanCreate(ScanBase):
    pass


class ScanOut(ScanBase):
    id: int
    user_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True