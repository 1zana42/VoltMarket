from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.items import ItemModel
    from app.models.users import UserModel


class PurchasesModel(Base):
    __tablename__ = "purchases"
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(nullable=False)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    item: Mapped["ItemModel"] = relationship(back_populates="purchases")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["UserModel"] = relationship(back_populates="purchases")