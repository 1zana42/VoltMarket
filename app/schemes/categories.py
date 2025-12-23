from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryGet(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryGetWithChildren(CategoryGet):
    children: List["CategoryGet"] = []
    item_count: int = 0