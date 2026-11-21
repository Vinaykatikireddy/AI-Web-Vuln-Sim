from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from schemas import lab as lab_schemas
from models import base
from services.lab_manager import LabManager

router = APIRouter(prefix="/api", tags=["lab"])

lab_manager = LabManager()


@router.get("/labs", response_model=List[lab_schemas.LabOut])
def get_labs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(base.Lab).offset(skip).limit(limit).all()


@router.get("/labs/{lab_id}", response_model=lab_schemas.LabOut)
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.api_route("/labs/start", methods=["GET", "POST"], response_model=lab_schemas.LabOut)
def start_lab(
    lab_id: Optional[int] = None,
    action: Optional[lab_schemas.LabAction] = Body(default=None),
    db: Session = Depends(get_db),
):
    target_id = action.lab_id if action and action.lab_id is not None else lab_id
    if target_id is None:
        raise HTTPException(status_code=400, detail="lab_id is required")
    lab = db.query(base.Lab).filter(base.Lab.id == target_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.api_route("/labs/stop", methods=["GET", "POST"], response_model=lab_schemas.LabOut)
def stop_lab(
    lab_id: Optional[int] = None,
    action: Optional[lab_schemas.LabAction] = Body(default=None),
    db: Session = Depends(get_db),
):
    target_id = action.lab_id if action and action.lab_id is not None else lab_id
    if target_id is None:
        raise HTTPException(status_code=400, detail="lab_id is required")
    lab = db.query(base.Lab).filter(base.Lab.id == target_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

    return lab