from typing import List, Optional
from sqlalchemy.orm import Session
from models import base


def create_log(db: Session, log: base.Log) -> base.Log:
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception:
        db.rollback()
        raise


def get_log(db: Session, log_id: int) -> Optional[base.Log]:
    return (
        db.query(base.Log)
        .filter(base.Log.id == log_id)
        .first()
    )


def get_logs(db: Session, skip: int = 0, limit: int = 100) -> List[base.Log]:
    return (
        db.query(base.Log)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_logs_by_scan_id(
    db: Session, scan_id: int
) -> List[base.Log]:
    return (
        db.query(base.Log)
        .filter(base.Log.scan_id == scan_id)
        .order_by(base.Log.timestamp.desc())
        .all()
    )


def get_logs_by_result(
    db: Session, result: str
) -> List[base.Log]:
    return (
        db.query(base.Log)
        .filter(base.Log.result == result)
        .all()
    )


def get_logs_by_severity(
    db: Session, severity: str
) -> List[base.Log]:
    return (
        db.query(base.Log)
        .filter(base.Log.severity == severity)
        .all()
    )


def delete_log(
    db: Session, log_id: int
) -> bool:
    log = get_log(db, log_id)
    if not log:
        return False
    try:
        db.delete(log)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def delete_logs_by_scan_id(
    db: Session, scan_id: int
) -> int:
    logs = (
        db.query(base.Log)
        .filter(base.Log.scan_id == scan_id)
        .all()
    )
    count = len(logs)
    try:
        for log in logs:
            db.delete(log)
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
