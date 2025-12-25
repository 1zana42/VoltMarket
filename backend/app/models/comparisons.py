from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.items import ItemModel


class ComparisonModel(Base):
    __tablename__ = "comparisons"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)  # Название сравнения
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    user: Mapped["UserModel"] = relationship(back_populates="comparisons")
    items: Mapped[list["ComparisonItemModel"]] = relationship(back_populates="comparison")


class ComparisonItemModel(Base):
    __tablename__ = "comparison_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    comparison_id: Mapped[int] = mapped_column(ForeignKey("comparisons.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    
    comparison: Mapped["ComparisonModel"] = relationship(back_populates="items")
    item: Mapped["ItemModel"] = relationship(back_populates="comparison_items")