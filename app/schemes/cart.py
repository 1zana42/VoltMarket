from typing import List
from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    item_id: int
    quantity: int = Field(..., ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemGet(BaseModel):
    id: int
    item_id: int
    item_name: str
    item_price: int
    item_image_url: Optional[str]
    quantity: int
    total_price: int
    
    class Config:
        from_attributes = True


class CartGet(BaseModel):
    items: List[CartItemGet] = []
    total_items: int = 0
    total_amount: int = 0