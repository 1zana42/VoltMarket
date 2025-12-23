from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.items import ItemModel
    from app.models.specification_types import SpecificationTypeModel


class SpecificationModel(Base):
    __tablename__ = "specifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    specification_type_id: Mapped[int] = mapped_column(ForeignKey("specification_types.id"), nullable=False)
    
    item: Mapped["ItemModel"] = relationship(back_populates="specifications")
    specification_type: Mapped["SpecificationTypeModel"] = relationship(back_populates="specifications")