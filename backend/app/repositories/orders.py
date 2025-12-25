from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from app.models.orders import OrderModel, OrderStatus
from app.models.order_items import OrderItemModel
from app.models.items import ItemModel
from app.repositories.base import BaseRepository
from app.schemes.orders import OrderGet, OrderItemGet


class OrdersRepository(BaseRepository):
    model = OrderModel
    schema = OrderGet

    async def add_order(self, user_id: int, total_amount: int, shipping_address: str, 
                       contact_phone: str, notes: str = None):
        """Создание нового заказа"""
        order_data = {
            "user_id": user_id,
            "total_amount": total_amount,
            "shipping_address": shipping_address,
            "contact_phone": contact_phone,
            "notes": notes,
            "status": OrderStatus.PENDING.value
        }
        
        return await self.add(order_data)

    async def get_user_orders(self, user_id: int, limit: int = 10, offset: int = 0):
        """Получение заказов пользователя"""
        query = (
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        orders = result.scalars().all()
        
        return [self.schema.model_validate(order, from_attributes=True) for order in orders]

    async def get_order_with_items(self, user_id: int, order_id: int):
        """Получение заказа с товарами"""
        query = (
            select(self.model)
            .options(selectinload(self.model.items).joinedload(OrderItemModel.item))
            .filter_by(id=order_id, user_id=user_id)
        )
        
        result = await self.session.execute(query)
        order = result.scalars().one_or_none()
        
        if not order:
            return None
        
        # Формируем данные заказа
        order_data = self.schema.model_validate(order, from_attributes=True)
        
        # Добавляем информацию о товарах
        order_data.items = []
        for order_item in order.items:
            item_data = OrderItemGet(
                id=order_item.id,
                item_id=order_item.item_id,
                item_name=order_item.item.name,
                quantity=order_item.quantity,
                price_at_purchase=order_item.price_at_purchase
            )
            order_data.items.append(item_data)
        
        return order_data

    async def count_user_orders(self, user_id: int) -> int:
        """Подсчет количества заказов пользователя"""
        query = select(func.count(self.model.id)).filter_by(user_id=user_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update_status(self, order_id: int, status: str):
        """Обновление статуса заказа"""
        await self.edit({"status": status}, id=order_id)

    async def has_user_purchased_item(self, user_id: int, item_id: int) -> bool:
        """Проверка, покупал ли пользователь товар"""
        query = (
            select(func.count(OrderItemModel.id))
            .join(OrderModel)
            .where(
                OrderModel.user_id == user_id,
                OrderItemModel.item_id == item_id,
                OrderModel.status == OrderStatus.DELIVERED.value
            )
        )
        
        result = await self.session.execute(query)
        count = result.scalar() or 0
        return count > 0