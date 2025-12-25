from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    description: str = Field(..., min_length=10, max_length=500)
    item_id: int


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = Field(None, min_length=10, max_length=500)


class ReviewGet(ReviewBase):
    id: int
    user_id: int
    user_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True