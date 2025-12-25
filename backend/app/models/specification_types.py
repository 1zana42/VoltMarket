from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.specifications import SpecificationModel
    from app.models.categories import CategoryModel


class SpecificationTypeModel(Base):
    __tablename__ = "specification_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Например: "Процессор"
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Например: "ГГц", "ГБ"
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    
    specifications: Mapped[list["SpecificationModel"]] = relationship(back_populates="specification_type")
    category: Mapped["CategoryModel"] = relationship()