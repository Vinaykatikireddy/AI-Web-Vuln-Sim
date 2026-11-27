from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from schemas import lab as lab_schemas
from models import base
from core import security
from services.lab_manager import LabManager

router = APIRouter()

lab_manager = LabManager()


@router.get("/labs", response_model=List[lab_schemas.LabOut])
def get_labs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(base.Lab).offset(skip).limit(limit).all()


@router.get("/labs/{lab_id}", response_model=lab_schemas.LabOut)
def get_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user),
):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    is_completed = (
        db.query(base.LabCompletion)
        .filter(
            base.LabCompletion.user_id == current_user.id,
            base.LabCompletion.lab_id == lab_id,
        )
        .first()
        is not None
    )
    lab_out = lab_schemas.LabOut.model_validate(lab)
    lab_out.completed = is_completed
    return lab_out


@router.post("/labs/{lab_id}/complete", response_model=lab_schemas.LabCompletionOut)
def toggle_lab_completion(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user),
):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    existing = (
        db.query(base.LabCompletion)
        .filter(
            base.LabCompletion.user_id == current_user.id,
            base.LabCompletion.lab_id == lab_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return lab_schemas.LabCompletionOut(lab_id=lab_id, completed=False)

    completion = base.LabCompletion(user_id=current_user.id, lab_id=lab_id)
    db.add(completion)
    db.commit()
    return lab_schemas.LabCompletionOut(lab_id=lab_id, completed=True)


@router.api_route("/labs/start", methods=["GET", "POST"], response_model=lab_schemas.LabOut)
def start_lab(
    lab_id: Optional[int] = None,
    action: Optional[lab_schemas.LabAction] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user),
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
    current_user: base.User = Depends(security.get_current_active_user),
):
    target_id = action.lab_id if action and action.lab_id is not None else lab_id
    if target_id is None:
        raise HTTPException(status_code=400, detail="lab_id is required")
    lab = db.query(base.Lab).filter(base.Lab.id == target_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

    return lab