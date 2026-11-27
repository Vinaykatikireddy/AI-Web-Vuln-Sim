from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
import re


def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', v):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', v):
        raise ValueError('Password must contain at least one digit')
    return v


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_strength(cls, v):
        return validate_password_strength(v)


class PasswordChange(BaseModel):
    new_password: str

    @field_validator('new_password')
    def password_strength(cls, v):
        return validate_password_strength(v)


class AccountDelete(BaseModel):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    message: str