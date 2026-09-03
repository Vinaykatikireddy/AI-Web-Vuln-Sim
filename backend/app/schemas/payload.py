from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class PayloadBase(BaseModel):
    category: str
    payload: str
    description: Optional[str] = None
    is_active: bool = True


class PayloadCreate(PayloadBase):
    pass


class PayloadUpdate(BaseModel):
    category: Optional[str] = None
    payload: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PayloadOut(PayloadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True