from pydantic import BaseModel
from typing import Optional


class ReportBase(BaseModel):
    scan_id: int
    format: str = "html"
    content: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportOut(ReportBase):
    id: int
    user_id: int
    generated_at: str
    status: str

    class Config:
        orm_mode = True


class ReportDetail(ReportOut):
    content: str
    scan: dict
    user: dict