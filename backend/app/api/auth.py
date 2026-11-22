from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import user as user_schemas
from core import security
from core.limiter import limiter

router = APIRouter(prefix="/auth")


def get_user_by_username(db: Session, username: str):
    return db.query(base.User).filter(base.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(base.User).filter(base.User.email == email).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.password_hash):
        return False
    return user


@router.post("/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create new user
    hashed_password = security.get_password_hash(user.password)
    
    db_user = base.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "Account created successfully. Please login."}

@router.post("/login", response_model=dict)
@limiter.limit("8/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    # Create access token
    access_token = security.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


@router.patch("/update-user")
def update_user(user_update: user_schemas.UserBase,current_user: base.User = Depends(security.get_current_active_user),db: Session = Depends(get_db)):
    updates = user_update.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    for field, value in updates.items():
        if value is None or not value.strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field} cannot be empty")

    if "username" in updates:
        if updates["username"] != current_user.username:
            if get_user_by_username(db, username=updates["username"]):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    if "email" in updates:
        if updates["email"] != current_user.email:
            if get_user_by_email(db, email=updates["email"]):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    try:
        for field, value in updates.items():
            setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    except Exception:
        db.rollback()
        raise

    return current_user


@router.get("/me")
def get_current_user(current_user: base.User = Depends(security.get_current_active_user)):
    return current_user
