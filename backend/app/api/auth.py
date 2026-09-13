from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import base
from schemas import user as user_schemas
from core import security
from core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    print("registering...")
    from time import perf_counter

    start = perf_counter()

    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    print("db_username:", perf_counter() - start)
    start = perf_counter()
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    print("db_useremail:", perf_counter() - start)
    # Create new user
    h = perf_counter()
    hashed_password = security.get_password_hash(user.password)
    print("total:", perf_counter() - h)
    add = perf_counter()
    db_user = base.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    print("total:", perf_counter() - add)
    commit = perf_counter()
    db.commit()
    print("total:", perf_counter() - commit)
    refresh = perf_counter()
    db.refresh(db_user)
    print("total:", perf_counter() - refresh)

    return db_user

@router.post("/login", response_model=dict)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print("logging...")
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    # Create access token
    access_token = security.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schemas.UserOut)
def get_current_user(current_user: base.User = Depends(security.get_current_active_user)):
    return current_user
