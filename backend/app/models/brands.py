from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.items import ItemModel

class BrandModel(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    items: Mapped[list["ItemModel"]] = relationship(back_populates="brand")