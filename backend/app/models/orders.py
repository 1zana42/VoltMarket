from typing import TYPE_CHECKING
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.order_items import OrderItemModel


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderModel(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    shipping_address: Mapped[str] = mapped_column(String(500), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    user: Mapped["UserModel"] = relationship()
    items: Mapped[list["OrderItemModel"]] = relationship(back_populates="order")