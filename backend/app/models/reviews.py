from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.items import ItemModel

class ReviewModel(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["UserModel"] = relationship(back_populates="reviews")

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    item: Mapped["ItemModel"] = relationship(back_populates="reviews")