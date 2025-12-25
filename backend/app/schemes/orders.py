from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(..., ge=1)


class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=5, max_length=500)
    contact_phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    notes: Optional[str] = Field(None, max_length=1000)
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = Field(None, min_length=5, max_length=500)
    contact_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')


class OrderItemGet(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    price_at_purchase: int
    
    class Config:
        from_attributes = True


class OrderGet(BaseModel):
    id: int
    user_id: int
    total_amount: int
    status: OrderStatus
    shipping_address: str
    contact_phone: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemGet] = []
    
    class Config:
        from_attributes = True