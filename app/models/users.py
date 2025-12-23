from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel
    from app.models.order_items import OrderItemModel
    from app.models.reviews import ReviewModel
    from app.models.orders import OrderModel
    from app.models.comparisons import ComparisonModel
    from app.models.cart import CartItemModel


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Добавил телефон
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Добавил адрес

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["RoleModel"] = relationship(back_populates="users")

    # Обновлённые связи
    reviews: Mapped[list["ReviewModel"]] = relationship(back_populates="user")
    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")
    comparisons: Mapped[list["ComparisonModel"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItemModel"]] = relationship(back_populates="user")