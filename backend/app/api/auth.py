from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import base
from app.schemas import user as user_schemas
from app.core import security
from app.cruds import user as user_crud

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = security.get_password_hash(user.password)
    db_user = base.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=dict)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_crud.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = security.create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schemas.UserOut)
def get_current_user(
    current_user: base.User = Depends(security.get_current_active_user),
):
    return current_user