from sqlalchemy.orm import Session
from models import base
from schemas import user as user_schemas
from core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str):
    return db.query(base.User).filter(base.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(base.User).filter(base.User.email == email).first()


def create_user(db: Session, user: user_schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = base.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user
