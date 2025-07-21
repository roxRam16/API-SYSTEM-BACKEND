from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from src.models.base import BaseDocument
from datetime import datetime

class Supplier(BaseDocument):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: str = Field(..., min_length=1, max_length=200)
    tax_id: str = Field(..., min_length=1, max_length=50)
    contact_person: str = Field(..., min_length=1, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    payment_terms: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = Field(default=0.0, ge=0)
    current_balance: float = Field(default=0.0)
    notes: Optional[str] = Field(None, max_length=500)

class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: str = Field(..., min_length=1, max_length=200)
    tax_id: str = Field(..., min_length=1, max_length=50)
    contact_person: str = Field(..., min_length=1, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    payment_terms: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None,pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_id: Optional[str] = Field(None, min_length=1, max_length=50)
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    payment_terms: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class SupplierResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: EmailStr
    phone: str
    address: str
    tax_id: str
    contact_person: str
    website: Optional[str]
    payment_terms: Optional[str]
    credit_limit: float
    current_balance: float
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Config:
    populate_by_name = True  # 👈 habilita alias inverso