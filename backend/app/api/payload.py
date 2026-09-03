from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import payload as payload_schemas
from core import security


router = APIRouter(prefix="/api", tags=["payloads"])


def get_payload(db: Session, payload_id: int):
    return db.query(base.Payload).filter(base.Payload.id == payload_id).first()


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


@router.get("/payloads", response_model=list[payload_schemas.PayloadOut])
def get_payloads(category: str = None, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    if category:
        return db.query(base.Payload).filter(base.Payload.category == category, base.Payload.is_active == True).all()
    else:
        return db.query(base.Payload).offset(skip).limit(limit).all()


@router.get("/payloads/{payload_id}", response_model=payload_schemas.PayloadOut)
def get_payload_info(payload_id: int, db: Session = Depends(get_db)):
    payload = get_payload(db, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return payload


@router.post("/payloads", response_model=payload_schemas.PayloadOut, status_code=status.HTTP_201_CREATED)
def create_payload_in_db(payload: payload_schemas.PayloadCreate, db: Session = Depends(get_db)):
    # Validate category
    valid_categories = [
        "sqli", "xss", "idor", "auth-bypass", "dir-traversal", "file-upload"
    ]
    if payload.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}"
        )

    # Create payload
    return create_payload(db, payload)


@router.put("/payloads/{payload_id}", response_model=payload_schemas.PayloadOut)
def update_payload(payload_id: int, payload: payload_schemas.PayloadUpdate, db: Session = Depends(get_db)):
    if payload.category is not None:
        valid_categories = [
            "sqli", "xss", "idor", "auth-bypass", "dir-traversal", "file-upload"
        ]
        if payload.category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}")

    updated_payload = update_payload(db, payload_id, payload)
    if not updated_payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return updated_payload


@router.delete("/payloads/{payload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payload(payload_id: int, db: Session = Depends(get_db)):
    deleted_payload = delete_payload(db, payload_id)
    if not deleted_payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return None
