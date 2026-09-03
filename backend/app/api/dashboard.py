from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import scan as scan_schemas
from core import security

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard", response_model=dict)
def get_dashboard(current_user: base.User = Depends(security.get_current_active_user), db: Session = Depends(get_db)):
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


@router.get("/scans/history", response_model=list[scan_schemas.ScanOut])
def get_scan_history(current_user: base.User = Depends(security.get_current_active_user), db: Session = Depends(get_db)):
    scans = db.query(base.Scan).filter(base.Scan.user_id == current_user.id).order_by(base.Scan.created_at.desc()).all()
    return scans
