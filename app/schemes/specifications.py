from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemes.specification_types import SpecificationTypeGet


class SpecificationBase(BaseModel):
    value: str = Field(..., max_length=500)
    item_id: int
    specification_type_id: int


class SpecificationCreate(SpecificationBase):
    pass


class SpecificationGet(SpecificationBase):
    id: int
    specification_type: "SpecificationTypeGet"
    
    class Config:
        from_attributes = True