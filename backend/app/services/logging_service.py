import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.models import base
from app.database import get_db
from app.services.attack_engine import AttackEngine
import logging
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingService:
    def __init__(self):
        self.attack_engine = AttackEngine()

    def create_log_entry(self, scan_id: int, request: str, response: str, payload: str,
                        result: str, severity: str = "low", metadata: Optional[Dict] = None,
                        db: Session = None) -> base.Log:
        """
        Create a log entry for an attack attempt
        """
        if db is None:
            db = next(get_db())

        log_data = {
            "scan_id": scan_id,
            "request": request,
            "response": response,
            "payload": payload,
            "result": result,
            "severity": severity
        }

        if metadata:
            log_data["metadata"] = json.dumps(metadata)

        log_entry = base.Log(**log_data)
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return log_entry

    def get_logs_by_scan(self, scan_id: int, db: Session = None) -> List[base.Log]:
        """
        Get all logs for a specific scan
        """
        if db is None:
            db = next(get_db())

        logs = db.query(base.Log).filter(base.Log.scan_id == scan_id).all()
        return logs

    def get_logs_by_scan_and_result(self, scan_id: int, result: str, db: Session = None) -> List[base.Log]:
        """
        Get logs for a specific scan with a specific result type
        """
        if db is None:
            db = next(get_db())

        logs = db.query(base.Log).filter(
            base.Log.scan_id == scan_id,
            base.Log.result == result
        ).all()
        return logs

    def log_attack_attempt(self, scan_id: int, attack_type: str, payload: str,
                          request: str, response: str, success: bool = False,
                          db: Session = None) -> base.Log:
        """
        Log an attack attempt with proper result classification
        """
        if db is None:
            db = next(get_db())

        result = "vulnerability_detected" if success else "failure"
        severity = "high" if success else "low"

        log_entry = self.create_log_entry(
            scan_id=scan_id,
            request=request,
            response=response,
            payload=payload,
            result=result,
            severity=severity,
            db=db
        )

        return log_entry

    def log_vulnerability(self, scan_id: int, attack_type: str, payload: str,
                         request: str, response: str, evidence: Dict[str, Any],
                         db: Session = None) -> base.Log:
        """
        Log a confirmed vulnerability with detailed evidence
        """
        if db is None:
            db = next(get_db())

        result = "vulnerability_detected"
        severity = self._determine_severity(attack_type)

        # Create metadata for evidence
        metadata = {
            "evidence": evidence,
            "attack_type": attack_type,
            "timestamp": str(datetime.now())
        }

        log_entry = self.create_log_entry(
            scan_id=scan_id,
            request=request,
            response=response,
            payload=payload,
            result=result,
            severity=severity,
            metadata=metadata,
            db=db
        )

        return log_entry

    def _determine_severity(self, attack_type: str) -> str:
        """
        Determine severity level based on attack type
        """
        severe_attack_types = [
            "sql_injection", "auth_bypass", "dir_traversal",
            "file_upload_abuse", "idor"
        ]

        if attack_type in severe_attack_types:
            return "high"
        elif attack_type in ["reflected_xss", "stored_xss"]:
            return "medium"
        else:
            return "low"