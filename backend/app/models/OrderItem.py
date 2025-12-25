from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.items import ItemModel
    from app.models.users import UserModel
    from app.models.orders import OrderModel  


class OrderItemModel(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_purchase: Mapped[int] = mapped_column(nullable=False)
    
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    item: Mapped["ItemModel"] = relationship(back_populates="order_items")
    
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["OrderModel"] = relationship(back_populates="items")