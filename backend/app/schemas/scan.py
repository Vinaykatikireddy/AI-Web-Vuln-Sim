from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List, Any


class ScanBase(BaseModel):
    lab_id: int
    attack_type: str = "ai_autonomous"


class ScanCreate(ScanBase):
    focus: Optional[str] = None


class ScanInteract(BaseModel):
    message: str


class AgentStepOut(BaseModel):
    id: int
    scan_id: int
    step_number: int
    role: str
    phase: str
    thought: Optional[str] = None
    action_name: Optional[str] = None
    action_input: Optional[Any] = None
    observation: Optional[str] = None
    log_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanOut(ScanBase):
    id: int
    user_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanStepsOut(BaseModel):
    scan_id: int
    lab_id: int
    lab_name: str
    attack_type: str
    status: str
    steps: List[AgentStepOut]
    report_id: Optional[int] = None