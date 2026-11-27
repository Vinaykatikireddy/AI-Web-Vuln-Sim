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
# @limiter.limit("8/minute")
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

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "access_token": security.create_access_token(data={"sub": current_user.username}),
        "token_type": "bearer",
    }


@router.post("/change-password", response_model=user_schemas.UserResponse)
def change_password(
    password_data: user_schemas.PasswordChange,
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        current_user.password_hash = security.get_password_hash(password_data.new_password)
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise

    return {"message": "Password changed successfully."}


@router.post("/logout")
def logout(
    token: str = Depends(security.oauth2_scheme),
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    security.revoke_token(db, token)
    return {"message": "Logged out successfully."}


@router.delete("/delete-account", response_model=user_schemas.UserResponse)
def delete_account(
    delete_data: user_schemas.AccountDelete,
    token: str = Depends(security.oauth2_scheme),
    current_user: base.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
):
    if not security.verify_password(delete_data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    try:
        scan_ids = [
            scan.id
            for scan in db.query(base.Scan.id).filter(base.Scan.user_id == current_user.id).all()
        ]
        if scan_ids:
            db.query(base.Log).filter(base.Log.scan_id.in_(scan_ids)).delete(synchronize_session=False)
            db.query(base.Report).filter(base.Report.scan_id.in_(scan_ids)).delete(synchronize_session=False)
        db.query(base.Report).filter(base.Report.user_id == current_user.id).delete(synchronize_session=False)
        db.query(base.Scan).filter(base.Scan.user_id == current_user.id).delete(synchronize_session=False)
        db.delete(current_user)
        db.commit()
    except Exception:
        db.rollback()
        raise

    security.revoke_token(db, token)
    return {"message": "Account deleted successfully."}


@router.get("/me")
def get_current_user(current_user: base.User = Depends(security.get_current_active_user)):
    return current_user
