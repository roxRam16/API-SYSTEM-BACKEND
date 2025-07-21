from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum
from src.models.base import BaseDocument
from datetime import datetime

class CustomerType(str, Enum):
    INDIVIDUAL = "fisica"
    BUSINESS = "moral"

class Customer(BaseDocument):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: str = Field(..., min_length=1, max_length=200)
    tax_id: str = Field(..., min_length=1, max_length=50)
    customer_type: CustomerType = Field(default=CustomerType.BUSINESS)
    credit_limit: Optional[float] = Field(default=0.0, ge=0)
    current_balance: float = Field(default=0.0)
    notes: Optional[str] = Field(None, max_length=500)

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: str = Field(..., min_length=1, max_length=200)
    tax_id: str = Field(..., min_length=1, max_length=50)
    customer_type: CustomerType = CustomerType.INDIVIDUAL
    credit_limit: Optional[float] = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_id: Optional[str] = Field(None, min_length=1, max_length=50)
    customer_type: Optional[CustomerType] = None
    credit_limit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CustomerResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: EmailStr
    phone: Optional[str]
    address: str
    tax_id: str
    customer_type: CustomerType
    credit_limit: Optional[float] = Field(None, ge=0)
    current_balance: Optional[float] = Field(None, ge=0)
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Config:
    populate_by_name = True  # 👈 habilita alias inverso