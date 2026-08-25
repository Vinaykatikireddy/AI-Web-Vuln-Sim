from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import report as report_schemas
from cruds import report as report_crud
from cruds import scan as scan_crud
from services.report_generator import ReportGenerator
from core import security
from typing import Dict, Any
import json

router = APIRouter(prefix="/api", tags=["reports"])

report_generator = ReportGenerator()

@router.get("/reports/{report_id}", response_model=report_schemas.ReportDetail)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Get a specific security report
    """
    report = report_crud.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this report"
        )

    # Load scan and user data
    scan = scan_crud.get_scan(db, report.scan_id)
    user = db.query(base.User).filter(base.User.id == report.user_id).first()

    # Parse content if it's JSON
    try:
        content_data = json.loads(report.content) if report.content else {}
    except json.JSONDecodeError:
        content_data = report.content

    return {
        "id": report.id,
        "scan_id": report.scan_id,
        "user_id": report.user_id,
        "content": content_data,
        "format": report.format,
        "generated_at": report.generated_at,
        "status": report.status,
        "scan": {
            "id": scan.id,
            "lab_id": scan.lab_id,
            "attack_type": scan.attack_type,
            "status": scan.status,
            "created_at": scan.created_at
        } if scan else {},
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        } if user else {}
    }


@router.get("/reports", response_model=list[report_schemas.ReportOut])
def get_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Get all reports for the current user
    """
    return report_crud.get_reports_by_user(db, current_user.id, skip, limit)


@router.get("/reports/scan/{scan_id}", response_model=list[report_schemas.ReportOut])
def get_reports_by_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Get all reports for a specific scan
    """
    # Verify scan belongs to current user
    scan = scan_crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view reports for this scan"
        )

    return report_crud.get_reports_by_scan(db, scan_id)


@router.post("/reports/generate", response_model=Dict[str, Any])
def generate_report(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Generate a security report for a scan
    """
    scan_id = request.get("scan_id")
    format_type = request.get("format", "html")

    # Verify scan exists and belongs to user
    scan = scan_crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to generate report for this scan"
        )

    # Validate format
    valid_formats = ["html", "markdown", "pdf"]
    if format_type not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Valid formats: {', '.join(valid_formats)}"
        )

    # Generate report
    result = report_generator.generate_report(scan_id, format_type, db)
    return result


@router.post("/reports/generate/{scan_id}", response_model=Dict[str, Any])
def generate_report_by_scan_id(
    scan_id: int,
    format_type: str = "html",
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Generate a security report for a scan by scan_id
    """
    # Verify scan exists and belongs to user
    scan = scan_crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to generate report for this scan"
        )

    # Validate format
    valid_formats = ["html", "markdown", "pdf"]
    if format_type not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Valid formats: {', '.join(valid_formats)}"
        )

    # Generate report
    result = report_generator.generate_report(scan_id, format_type, db)
    return result
