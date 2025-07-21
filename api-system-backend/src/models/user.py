from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from enum import Enum
from src.models.base import BaseDocument
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    USER = "user"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class UserProfile(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)

class User(BaseDocument):
    email: EmailStr = Field(..., unique=True)
    username: str = Field(..., min_length=3, max_length=50, unique=True)
    hashed_password: str = Field(...)
    role: UserRole = Field(default=UserRole.USER)
    permissions: List[Permission] = Field(default=[Permission.READ])
    profile: UserProfile = Field(...)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0)
    is_locked: bool = Field(default=False)

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.USER
    permissions: List[Permission] = [Permission.READ]
    profile: UserProfile

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[UserRole] = None
    permissions: Optional[List[Permission]] = None
    profile: Optional[UserProfile] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    username: str
    role: UserRole
    permissions: List[Permission]
    profile: UserProfile
    is_active: bool
    is_verified: Optional[bool] = None   # ✅ Ahora opcional
    last_login: Optional[datetime] = None  # ✅ Ahora opcional
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token : str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class Config:
    populate_by_name = True  # 👈 habilita alias inverso