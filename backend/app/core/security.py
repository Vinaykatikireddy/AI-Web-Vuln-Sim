import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from models import base
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

# URL should match the route that issues tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
JWT_ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def _get_token_identifier(token: str, payload: dict) -> str:
    jti = payload.get("jti")
    if jti:
        return str(jti)
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_token_revoked(db: Session, token_id: str) -> bool:
    return (
        db.query(base.RevokedToken)
        .filter(base.RevokedToken.jti == token_id)
        .first()
        is not None
    )


def revoke_token(db: Session, token: str) -> None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return

    token_id = _get_token_identifier(token, payload)
    exp = payload.get("exp")
    expires_at = (
        datetime.fromtimestamp(exp, tz=timezone.utc)
        if exp is not None
        else datetime.now(timezone.utc) + timedelta(minutes=30)
    )

    if not is_token_revoked(db, token_id):
        db.query(base.RevokedToken).filter(
            base.RevokedToken.expires_at < datetime.now(timezone.utc)
        ).delete(synchronize_session=False)
        db.add(base.RevokedToken(jti=token_id, expires_at=expires_at))
        db.commit()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(base.User).filter(base.User.username == username).first()


def get_current_active_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if is_token_revoked(db, _get_token_identifier(token, payload)):
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
