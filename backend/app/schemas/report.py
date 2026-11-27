from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ReportBase(BaseModel):
    scan_id: int
    format: str = "html"
    content: Optional[Any] = None


class ReportOut(ReportBase):
    id: int
    user_id: int
    generated_at: datetime
    status: str

    class Config:
        from_attributes = True


class ReportDetail(ReportOut):
    content: Any
    scan: dict
    user: dict