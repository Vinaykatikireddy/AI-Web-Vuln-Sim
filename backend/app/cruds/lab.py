from sqlalchemy.orm import Session
from models import base
from schemas import lab as lab_schemas
from services.lab_manager import LabManager

lab_manager = LabManager()


def get_lab(db: Session, lab_id: int):
    return db.query(base.Lab).filter(base.Lab.id == lab_id).first()


def get_labs(db: Session, skip: int = 0, limit: int = 100):
    # Get available labs from LabManager
    available_labs = lab_manager.get_available_labs()

    # Create or update lab records in database
    for lab_data in available_labs:
        db_lab = db.query(base.Lab).filter(base.Lab.id == lab_data['id']).first()
        if not db_lab:
            db_lab = base.Lab(
                id=lab_data['id'],
                name=lab_data['name'],
                description=lab_data['description'],
                docker_image=lab_data['docker_image'],
                port=lab_data['port']
            )
            db.add(db_lab)

        # Update status
        status = lab_manager.get_lab_status(lab_data['id'])
        db_lab.status = status

    db.commit()
    return db.query(base.Lab).offset(skip).limit(limit).all()


def create_lab(db: Session, lab: lab_schemas.LabCreate):
    # This function can be used to add custom labs
    # For now, we'll use the predefined labs from LabManager
    db_lab = base.Lab(
        name=lab.name,
        description=lab.description,
        docker_image=lab.docker_image,
        port=lab.port,
        status="stopped"
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab


def update_lab_status(db: Session, lab_id: int, status: str):
    db_lab = get_lab(db, lab_id)
    if db_lab:
        db_lab.status = status
        db.commit()
        db.refresh(db_lab)
    return db_lab


def start_lab(db: Session, lab_id: int):
    success = lab_manager.start_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "running")
    return None


def stop_lab(db: Session, lab_id: int):
    success = lab_manager.stop_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "stopped")
    return None


def reset_lab(db: Session, lab_id: int):
    success = lab_manager.reset_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "running")
    return None


def delete_lab(db: Session, lab_id: int):
    success = lab_manager.delete_lab(lab_id)
    if success:
        return update_lab_status(db, lab_id, "deleted")
    return None
