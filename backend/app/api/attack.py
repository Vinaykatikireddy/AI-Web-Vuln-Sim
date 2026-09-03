from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import scan as scan_schemas
from services.attack_engine import AttackEngine
from core import security
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["attacks"])

attack_engine = AttackEngine()


def update_scan_status(db: Session, scan_id: int, status: str):
    db_scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if db_scan:
        db_scan.status = status
        db.commit()
        db.refresh(db_scan)
    return db_scan


@router.post("/scans/run", response_model=scan_schemas.ScanOut)
def run_attack_simulation(scan_data: scan_schemas.ScanCreate, current_user: base.User = Depends(security.get_current_active_user), db: Session = Depends(get_db)):
    # Validate the lab exists and is running
    lab = db.query(base.Lab).filter(base.Lab.id == scan_data.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    if lab.status != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Lab must be running to perform attacks. Current status: {lab.status}",
        )

    # Validate attack type
    valid_attack_types = [
        "sql_injection",
        "reflected_xss",
        "stored_xss",
        "idor",
        "auth_bypass",
        "dir_traversal",
        "file_upload_abuse",
    ]

    if scan_data.attack_type not in valid_attack_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attack type. Valid types: {', '.join(valid_attack_types)}",
        )

    # Create scan record
    scan = base.Scan(
            user_id=current_user.id,
            lab_id=scan.lab_id,
            attack_type=scan.attack_type,
            status="pending"
        )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    try:
        # Run the attack simulation
        attack_engine.run_attack_simulation(
            scan_data.attack_type, scan_data.lab_id, scan.id, db
        )

        # Update scan status to completed
        update_scan_status(db, scan.id, "completed")

        # Return the scan record with updated status
        updated_scan = db.query(base.Scan).filter(base.Scan.id == scan.id).first()
        return updated_scan

    except Exception:
        # Update scan status to failed
        update_scan_status(db, scan.id, "failed")
        logger.exception(f"Attack simulation failed for scan {scan.id}")
        raise HTTPException(status_code=500, detail="Attack simulation failed")

@router.get("/scans/{scan_id}/results", response_model=Dict[str, Any])
def get_attack_results(scan_id: int, current_user: base.User = Depends(security.get_current_active_user), db: Session = Depends(get_db)):
    scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these scan results"
        )

    # Get all logs for this scan
    logs = db.query(base.Log).filter(base.Log.scan_id == scan_id).all()

    # Check if attack was successful
    vulnerability_detected = any(log.result == "vulnerability_detected" for log in logs)

    # Create payload usage summary
    payloads_used = list(set(log.payload for log in logs if log.payload))
    successful_payloads = list(
        set(log.payload for log in logs if log.result == "vulnerability_detected")
    )

    return {
        "scan_id": scan_id,
        "attack_type": scan.attack_type,
        "lab_id": scan.lab_id,
        "user_id": scan.user_id,
        "status": scan.status,
        "started_at": scan.started_at,
        "completed_at": scan.completed_at,
        "vulnerability_detected": vulnerability_detected,
        "payloads_used": payloads_used,
        "successful_payloads": successful_payloads,
        "total_attempts": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "request": log.request,
                "response": log.response,
                "payload": log.payload,
                "result": log.result,
                "severity": log.severity,
            }
            for log in logs
        ],
    }
