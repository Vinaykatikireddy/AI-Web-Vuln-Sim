from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import lab as lab_schemas
from models import base
from services.lab_manager import LabManager

router = APIRouter(prefix="/api", tags=["lab"])

lab_manager = LabManager()

def update_lab_status(db: Session, lab_id: int, status: str):
    db_lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if db_lab:
        db_lab.status = status
        db.commit()
        db.refresh(db_lab)
    return db_lab


@router.get("/labs", response_model=list[lab_schemas.LabOut])
def get_labs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(base.Lab).offset(skip).limit(limit).all()


@router.get("/labs/{lab_id}", response_model=lab_schemas.LabOut)
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.post("/labs/start", response_model=lab_schemas.LabOut)
def start_lab(lab_id: int, db: Session = Depends(get_db)):
    success = lab_manager.start_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "running")
    else:
        raise HTTPException(status_code=404, detail="Lab not found or failed to start")


@router.post("/labs/stop", response_model=lab_schemas.LabOut)
def stop_lab(lab_id: int, db: Session = Depends(get_db)):
    success = lab_manager.stop_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "stopped")
    raise HTTPException(status_code=404, detail="Lab not found or failed to stop")


@router.post("/labs/reset", response_model=lab_schemas.LabOut)
def reset_lab(lab_id: int, db: Session = Depends(get_db)):
    success = lab_manager.reset_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "running")
    raise HTTPException(status_code=404, detail="Lab not found or failed to reset")


@router.post("/labs/delete", response_model=lab_schemas.LabOut)
def delete_lab(lab_id: int, db: Session = Depends(get_db)):
    success = lab_manager.delete_lab(db, lab_id)
    if success:
        return update_lab_status(db, lab_id, "deleted")
    raise HTTPException(status_code=404, detail="Lab not found or failed to delete")
