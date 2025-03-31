from pydantic import BaseModel, EmailStr, field_validator
from test_app.models.role import RoleEnum
from test_app.models.user import UserCreate,User
import re

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: RoleEnum

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # Complex password validation
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

class UserResponse(UserBase):
    id: int
    role: RoleEnum

    class Config:
        from_attributes = True
