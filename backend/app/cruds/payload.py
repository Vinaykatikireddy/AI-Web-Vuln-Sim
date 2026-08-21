from sqlalchemy.orm import Session
from app.models import base
from app.schemas import payload as payload_schemas

def get_payload(db: Session, payload_id: int):
    return db.query(base.Payload).filter(base.Payload.id == payload_id).first()


def get_payloads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(base.Payload).offset(skip).limit(limit).all()


def get_payloads_by_category(db: Session, category: str):
    return db.query(base.Payload).filter(base.Payload.category == category, base.Payload.is_active == True).all()


def create_payload(db: Session, payload: payload_schemas.PayloadCreate):
    db_payload = base.Payload(
        category=payload.category,
        payload=payload.payload,
        description=payload.description
    )
    db.add(db_payload)
    db.commit()
    db.refresh(db_payload)
    return db_payload


def update_payload(db: Session, payload_id: int, payload: payload_schemas.PayloadUpdate):
    db_payload = get_payload(db, payload_id)
    if db_payload:
        if payload.category is not None:
            db_payload.category = payload.category
        if payload.payload is not None:
            db_payload.payload = payload.payload
        if payload.description is not None:
            db_payload.description = payload.description
        if payload.is_active is not None:
            db_payload.is_active = payload.is_active
        db.commit()
        db.refresh(db_payload)
    return db_payload


def delete_payload(db: Session, payload_id: int):
    db_payload = get_payload(db, payload_id)
    if db_payload:
        db.delete(db_payload)
        db.commit()
    return db_payload