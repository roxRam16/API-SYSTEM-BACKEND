from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from src.models.base import BaseDocument
from datetime import datetime

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    CREDIT = "credit"

class SaleStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class SaleItem(BaseModel):
    product_id: str = Field(...)
    product_name: str = Field(...)
    sku: str = Field(...)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(default=0.0, ge=0)
    tax_rate: float = Field(default=0.0, ge=0, le=1)
    subtotal: float = Field(..., gt=0)
    tax_amount: float = Field(default=0.0, ge=0)
    total: float = Field(..., gt=0)

class Sale(BaseDocument):
    sale_number: str = Field(..., unique=True)
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    cashier_id: str = Field(...)
    cashier_name: str = Field(...)
    items: List[SaleItem] = Field(...)
    subtotal: float = Field(..., gt=0)
    discount_amount: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)
    total_amount: float = Field(..., gt=0)
    payment_method: PaymentMethod = Field(...)
    payment_reference: Optional[str] = Field(None)
    status: SaleStatus = Field(default=SaleStatus.PENDING)
    notes: Optional[str] = Field(None, max_length=500)
    sale_date: datetime = Field(default_factory=datetime.utcnow)

class SaleCreate(BaseModel):
    customer_id: str
    items: List[SaleItem]
    payment_method: PaymentMethod
    payment_reference: Optional[str] = None
    discount_amount: float = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class SaleUpdate(BaseModel):
    status: Optional[SaleStatus] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class SaleResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    sale_number: str
    customer_id: str
    customer_name: str
    cashier_id: str
    cashier_name: str
    items: List[SaleItem]
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: PaymentMethod
    payment_reference: Optional[str]
    status: SaleStatus
    notes: Optional[str]
    sale_date: datetime
    created_at: datetime
    updated_at: datetime

class Config:
    populate_by_name = True  # 👈 habilita alias inverso