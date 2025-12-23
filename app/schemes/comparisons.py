from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class ComparisonItemAdd(BaseModel):
    item_id: int


class ComparisonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ComparisonItemGet(BaseModel):
    id: int
    item_id: int
    item_name: str
    item_price: int
    item_image_url: Optional[str]
    
    class Config:
        from_attributes = True


class ComparisonGet(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime
    items: List[ComparisonItemGet] = []
    
    class Config:
        from_attributes = True