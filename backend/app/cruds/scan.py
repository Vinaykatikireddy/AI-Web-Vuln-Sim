from sqlalchemy.orm import Session
from models import base
from schemas import scan as scan_schemas
import datetime


def get_scan(db: Session, scan_id: int):
    return db.query(base.Scan).filter(base.Scan.id == scan_id).first()


def get_scans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(base.Scan).filter(base.Scan.user_id == user_id).offset(skip).limit(limit).all()


def create_scan(db: Session, scan: scan_schemas.ScanCreate, user_id: int):
    db_scan = base.Scan(
        user_id=user_id,
        lab_id=scan.lab_id,
        attack_type=scan.attack_type,
        status="pending"
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan


def update_scan_status(db: Session, scan_id: int, status: str):
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db_scan.status = status
        db.commit()
        db.refresh(db_scan)
    return db_scan


def complete_scan(db: Session, scan_id: int):
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db_scan.status = "completed"
        db_scan.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_scan)
    return db_scan
