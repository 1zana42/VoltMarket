from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.items import ItemModel

class CategoryModel(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    # Связи
    items: Mapped[list["ItemModel"]] = relationship(back_populates="category")
    children: Mapped[list["CategoryModel"]] = relationship(back_populates="parent")
    parent: Mapped["CategoryModel"] = relationship(back_populates="children", remote_side=[id])