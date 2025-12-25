from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.categories import CategoryModel
    from app.models.brands import BrandModel
    from app.models.order_items import OrderItemModel
    from app.models.reviews import ReviewModel
    from app.models.specifications import SpecificationModel
    from app.models.comparisons import ComparisonItemModel


class ItemModel(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # Артикул
    price: Mapped[int] = mapped_column(nullable=False)
    discount_price: Mapped[int | None] = mapped_column(nullable=True)  # Цена со скидкой
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    main_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Внешние ключи
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False)
    
    # Связи
    category: Mapped["CategoryModel"] = relationship(back_populates="items")
    brand: Mapped["BrandModel"] = relationship(back_populates="items")
    specifications: Mapped[list["SpecificationModel"]] = relationship(back_populates="item")
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="item")
    reviews: Mapped[list["ReviewModel"]] = relationship(back_populates="item")
    comparison_items: Mapped[list["ComparisonItemModel"]] = relationship(back_populates="item")
    
    # Вычисляемое свойство для среднего рейтинга (будет в сервисе)