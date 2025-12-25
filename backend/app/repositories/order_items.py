from sqlalchemy import select
from app.models.order_items import OrderItemModel
from app.repositories.base import BaseRepository


class OrderItemsRepository(BaseRepository):
    model = OrderItemModel
    schema = None  # Используется только через OrdersRepository

    async def add_order_item(self, order_id: int, item_id: int, quantity: int, price_at_purchase: int):
        """Добавление товара в заказ"""
        order_item_data = {
            "order_id": order_id,
            "item_id": item_id,
            "quantity": quantity,
            "price_at_purchase": price_at_purchase
        }
        
        return await self.add(order_item_data)

    async def get_by_order(self, order_id: int):
        """Получение товаров заказа"""
        query = select(self.model).filter_by(order_id=order_id)
        result = await self.session.execute(query)
        return result.scalars().all()