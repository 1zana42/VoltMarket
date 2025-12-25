from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BrandBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    logo_url: Optional[str] = None
    description: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    logo_url: Optional[str] = None
    description: Optional[str] = None


class BrandGet(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True