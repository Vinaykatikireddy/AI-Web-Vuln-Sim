from pydantic import BaseModel
from typing import Optional


class LabBase(BaseModel):
    name: str
    description: Optional[str] = None
    docker_image: str
    port: Optional[int] = None


class LabCreate(LabBase):
    pass


class LabOut(LabBase):
    id: int
    status: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True