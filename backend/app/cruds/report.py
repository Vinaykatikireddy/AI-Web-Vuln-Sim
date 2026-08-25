from sqlalchemy.orm import Session
from models import base
from schemas import report as report_schemas


def get_report(db: Session, report_id: int):
    return db.query(base.Report).filter(base.Report.id == report_id).first()


def get_reports_by_scan(db: Session, scan_id: int):
    return db.query(base.Report).filter(base.Report.scan_id == scan_id).all()


def get_reports_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(base.Report).filter(base.Report.user_id == user_id).offset(skip).limit(limit).all()


def create_report(db: Session, report: report_schemas.ReportCreate):
    db_report = base.Report(
        scan_id=report.scan_id,
        user_id=report.user_id,
        content=report.content,
        format=report.format,
        status=report.status
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def update_report_status(db: Session, report_id: int, status: str):
    db_report = get_report(db, report_id)
    if db_report:
        db_report.status = status
        db.commit()
        db.refresh(db_report)
    return db_report


def delete_report(db: Session, report_id: int):
    db_report = get_report(db, report_id)
    if db_report:
        db.delete(db_report)
        db.commit()
    return db_report
