from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import scan as scan_schemas
from services.attack_engine import AttackEngine
from services.ai_agent import AIAgentRunner
from core import security
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

attack_engine = AttackEngine()
ai_agent_runner = AIAgentRunner()


def update_scan_status(db: Session, scan_id: int, status: str):
    db_scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if db_scan:
        db_scan.status = status
        db.commit()
        db.refresh(db_scan)
    return db_scan


@router.post("/scans/run", response_model=scan_schemas.ScanOut)
def run_attack_simulation(
    scan_data: scan_schemas.ScanCreate,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    # Validate the lab exists (external labs are always active)
    lab = db.query(base.Lab).filter(base.Lab.id == scan_data.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

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
        lab_id=scan_data.lab_id,
        attack_type=scan_data.attack_type,
        status="pending",
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
def get_attack_results(
    scan_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
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


def _serialize_scan_steps(db: Session, scan: base.Scan) -> scan_schemas.ScanStepsOut:
    steps = (
        db.query(base.AgentStep)
        .filter(base.AgentStep.scan_id == scan.id)
        .order_by(base.AgentStep.step_number.asc())
        .all()
    )
    serialized_steps = []
    for step in steps:
        parsed_input = None
        if step.action_input:
            try:
                parsed_input = json.loads(step.action_input)
            except json.JSONDecodeError:
                parsed_input = step.action_input
        serialized_steps.append(
            scan_schemas.AgentStepOut(
                id=step.id,
                scan_id=step.scan_id,
                step_number=step.step_number,
                role=step.role,
                phase=step.phase,
                thought=step.thought,
                action_name=step.action_name,
                action_input=parsed_input,
                observation=step.observation,
                log_id=step.log_id,
                created_at=step.created_at,
            )
        )
    report = db.query(base.Report).filter(base.Report.scan_id == scan.id).first()
    return scan_schemas.ScanStepsOut(
        scan_id=scan.id,
        lab_id=scan.lab_id,
        lab_name=scan.lab.name if scan.lab else "Lab",
        attack_type=scan.attack_type,
        status=scan.status,
        steps=serialized_steps,
        report_id=report.id if report else None,
    )


@router.get("/scans/{scan_id}", response_model=Dict[str, Any])
def get_scan(
    scan_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")
    return {
        "id": scan.id,
        "lab_id": scan.lab_id,
        "user_id": scan.user_id,
        "attack_type": scan.attack_type,
        "status": scan.status,
        "started_at": scan.started_at,
        "completed_at": scan.completed_at,
        "created_at": scan.created_at,
        "lab": {
            "id": scan.lab.id,
            "name": scan.lab.name,
            "external_url": scan.lab.external_url,
        }
        if scan.lab
        else None,
    }


@router.post("/scans/ai/run", response_model=scan_schemas.ScanOut)
def run_ai_autonomous_scan(
    scan_data: scan_schemas.ScanCreate,
    background_tasks: BackgroundTasks,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    lab = db.query(base.Lab).filter(base.Lab.id == scan_data.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    scan = base.Scan(
        user_id=current_user.id,
        lab_id=scan_data.lab_id,
        attack_type=scan_data.attack_type or "ai_autonomous",
        status="pending",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    background_tasks.add_task(ai_agent_runner.run_autonomous_scan_sync, scan.id, scan_data.focus)
    return scan


@router.get("/scans/{scan_id}/steps", response_model=scan_schemas.ScanStepsOut)
def get_scan_steps(
    scan_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")
    return _serialize_scan_steps(db, scan)


@router.post("/scans/{scan_id}/interact", response_model=scan_schemas.ScanStepsOut)
async def interact_with_scan(
    scan_id: int,
    payload: scan_schemas.ScanInteract,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to interact with this scan")
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    await ai_agent_runner.interact(db, scan, payload.message.strip())
    return _serialize_scan_steps(db, scan)


@router.post("/scans/{scan_id}/report", response_model=Dict[str, Any])
async def generate_scan_report(
    scan_id: int,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to generate report for this scan")

    report = await ai_agent_runner.generate_structured_report(db, scan)
    return {"report_id": report.id, "scan_id": scan.id, "status": report.status}
