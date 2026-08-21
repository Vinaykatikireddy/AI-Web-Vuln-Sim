from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import base
from app.schemas import lab as lab_schemas, scan as scan_schemas
from app.core import security

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard", response_model=dict)
def get_dashboard(
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user statistics
    total_scans = db.query(base.Scan).filter(base.Scan.user_id == current_user.id).count()
    completed_scans = db.query(base.Scan).filter(
        base.Scan.user_id == current_user.id,
        base.Scan.status == "completed"
    ).count()

    # Get active labs
    active_labs = db.query(base.Lab).filter(base.Lab.status == "running").all()

    # Get recent scans
    recent_scans = db.query(base.Scan).filter(
        base.Scan.user_id == current_user.id
    ).order_by(base.Scan.created_at.desc()).limit(5).all()

    # Get AI reports
    recent_reports = db.query(base.Report).join(base.Scan).filter(
        base.Scan.user_id == current_user.id
    ).order_by(base.Report.generated_at.desc()).limit(5).all()

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_scans": total_scans,
        "completed_scans": completed_scans,
        "active_labs": len(active_labs),
        "recent_scans": [
            {
                "id": scan.id,
                "lab_name": scan.lab.name,
                "attack_type": scan.attack_type,
                "status": scan.status,
                "created_at": scan.created_at.isoformat()
            } for scan in recent_scans
        ],
        "recent_reports": [
            {
                "id": report.id,
                "scan_id": report.scan_id,
                "format": report.format,
                "generated_at": report.generated_at.isoformat(),
                "status": report.status
            } for report in recent_reports
        ]
    }


@router.get("/labs", response_model=list[lab_schemas.LabOut])
def get_labs(
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get all available labs
    labs = db.query(base.Lab).all()
    return labs


@router.get("/labs/{lab_id}", response_model=lab_schemas.LabOut)
def get_lab(
    lab_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


@router.post("/labs/start", response_model=dict)
def start_lab(
    lab_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    # In a real implementation, this would start the Docker container
    # For now, we'll just update the status
    lab.status = "running"
    db.commit()
    db.refresh(lab)

    return {"message": f"Lab {lab.name} started successfully", "lab": lab}


@router.post("/labs/stop", response_model=dict)
def stop_lab(
    lab_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    lab = db.query(base.Lab).filter(base.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    # In a real implementation, this would stop the Docker container
    # For now, we'll just update the status
    lab.status = "stopped"
    db.commit()
    db.refresh(lab)

    return {"message": f"Lab {lab.name} stopped successfully", "lab": lab}


@router.get("/scans/history", response_model=list[scan_schemas.ScanOut])
def get_scan_history(
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    scans = db.query(base.Scan).filter(base.Scan.user_id == current_user.id).order_by(base.Scan.created_at.desc()).all()
    return scans