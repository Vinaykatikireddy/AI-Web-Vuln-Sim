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
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True