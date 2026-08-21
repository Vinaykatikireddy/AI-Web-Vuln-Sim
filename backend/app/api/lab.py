from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import lab as lab_schemas
from app.cruds import lab as lab_crud

router = APIRouter(prefix="/api", tags=["lab"])

@router.get("/labs", response_model=list[lab_schemas.LabOut])
def get_labs(
    db: Session = Depends(get_db)
):
    """Get all available vulnerable labs"""
    return lab_crud.get_labs(db)


@router.get("/labs/{lab_id}", response_model=lab_schemas.LabOut)
def get_lab(
    lab_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific vulnerable lab"""
    lab = lab_crud.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.post("/labs/start", response_model=lab_schemas.LabOut)
def start_lab(
    lab_id: int,
    db: Session = Depends(get_db)
):
    """Start a vulnerable lab"""
    lab = lab_crud.start_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found or failed to start")
    return lab


@router.post("/labs/stop", response_model=lab_schemas.LabOut)
def stop_lab(
    lab_id: int,
    db: Session = Depends(get_db)
):
    """Stop a vulnerable lab"""
    lab = lab_crud.stop_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found or failed to stop")
    return lab


@router.post("/labs/reset", response_model=lab_schemas.LabOut)
def reset_lab(
    lab_id: int,
    db: Session = Depends(get_db)
):
    """Reset a vulnerable lab to its initial state"""
    lab = lab_crud.reset_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found or failed to reset")
    return lab


@router.post("/labs/delete", response_model=lab_schemas.LabOut)
def delete_lab(
    lab_id: int,
    db: Session = Depends(get_db)
):
    """Delete a vulnerable lab"""
    lab = lab_crud.delete_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found or failed to delete")
    return lab