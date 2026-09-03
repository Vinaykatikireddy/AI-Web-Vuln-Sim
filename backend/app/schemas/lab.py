from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class LabBase(BaseModel):
    name: str
    description: Optional[str] = None
    docker_image: Optional[str] = None
    port: Optional[int] = None
    external_url: Optional[str] = None


class LabOut(LabBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True