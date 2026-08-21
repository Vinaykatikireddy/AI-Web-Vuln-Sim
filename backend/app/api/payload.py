from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import base
from app.schemas import payload as payload_schemas
from app.cruds import payload as payload_crud
from app.core import security

router = APIRouter(prefix="/api", tags=["payloads"])

@router.get("/payloads", response_model=list[payload_schemas.PayloadOut])
def get_payloads(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Get all payloads, optionally filtered by category
    """
    if category:
        payloads = payload_crud.get_payloads_by_category(db, category)
    else:
        payloads = payload_crud.get_payloads(db)
    return payloads


@router.get("/payloads/{payload_id}", response_model=payload_schemas.PayloadOut)
def get_payload(
    payload_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Get a specific payload by ID
    """
    payload = payload_crud.get_payload(db, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return payload


@router.post("/payloads", response_model=payload_schemas.PayloadOut, status_code=status.HTTP_201_CREATED)
def create_payload(
    payload: payload_schemas.PayloadCreate,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Create a new payload
    """
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
    return payload_crud.create_payload(db, payload)


@router.put("/payloads/{payload_id}", response_model=payload_schemas.PayloadOut)
def update_payload(
    payload_id: int,
    payload: payload_schemas.PayloadUpdate,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Update a specific payload
    """
    if payload.category is not None:
        valid_categories = [
            "sqli", "xss", "idor", "auth-bypass", "dir-traversal", "file-upload"
        ]
        if payload.category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}"
            )

    updated_payload = payload_crud.update_payload(db, payload_id, payload)
    if not updated_payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return updated_payload


@router.delete("/payloads/{payload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payload(
    payload_id: int,
    db: Session = Depends(get_db),
    current_user: base.User = Depends(security.get_current_active_user)
):
    """
    Delete a specific payload
    """
    deleted_payload = payload_crud.delete_payload(db, payload_id)
    if not deleted_payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return None