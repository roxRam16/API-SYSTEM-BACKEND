from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from src.models.base import BaseDocument
from datetime import datetime

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class Product(BaseDocument):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, min_length=1, max_length=50, unique=True)
    barcode: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(default=1, ge=0)
    min_stock_level: Optional[int] = Field(default=10, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    supplier_id: Optional[str] = None
    tax_rate: Optional[float] = Field(default=0.0, ge=0, le=1)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    image_urls: List[str] = Field(default=[])
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    tags: List[str] = Field(default=[])

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float]= Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(default=10, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    supplier_id: Optional[str] = None
    tax_rate: Optional[float] = Field(default=0.0, ge=0, le=1)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    image_urls: List[str] = Field(default=[])
    tags: List[str] = Field(default=[])

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    supplier_id: Optional[str] = None
    tax_rate: Optional[float] = Field(None, ge=0, le=1)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    image_urls: Optional[List[str]] = None
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    category: Optional[str]
    brand: Optional[str]
    unit_price: Optional[float]
    cost_price: Optional[float]
    stock_quantity: Optional[int]
    min_stock_level: Optional[int]
    max_stock_level: Optional[int]
    supplier_id: Optional[str]
    tax_rate: Optional[float]
    weight: Optional[float]
    dimensions: Optional[str]
    image_urls: List[str]
    tags: List[str]
    status: Optional[ProductStatus] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    #status: ProductStatus

class Config:
    populate_by_name = True  # 👈 habilita alias inverso