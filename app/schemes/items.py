from typing import TYPE_CHECKING, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from app.schemes.categories import CategoryGet
    from app.schemes.brands import BrandGet
    from app.schemes.specifications import SpecificationGet


class ItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    price: int = Field(..., ge=0)
    discount_price: Optional[int] = Field(None, ge=0)
    quantity: int = Field(..., ge=0)
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    category_id: int
    brand_id: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    price: Optional[int] = Field(None, ge=0)
    discount_price: Optional[int] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    main_image_url: Optional[str] = None


class ItemGet(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemGetWithRelations(ItemGet):
    category: "CategoryGet"
    brand: "BrandGet"
    specifications: List["SpecificationGet"] = []
    average_rating: Optional[float] = None
    review_count: int = 0


class ItemSearchParams(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    in_stock: Optional[bool] = None
    sort_by: Optional[str] = Field(None, pattern="^(price|name|created_at|rating)$")
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")