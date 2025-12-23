from typing import List
from sqlalchemy import select

from app.exceptions.base import ObjectNotFoundError
from app.schemes.orders import OrderCreate, OrderGet, OrderItemGet
from app.services.base import BaseService


class OrdersService(BaseService):
    
    async def create_order(self, user_id: int, order_data: OrderCreate) -> int:
        """Создание нового заказа из корзины"""
        # Получаем корзину пользователя
        cart_items = await self.db.cart_items.get_user_cart(user_id)
        
        if not cart_items:
            raise ValueError("Корзина пуста")
        
        # Проверяем наличие товаров и их количество
        for cart_item in cart_items:
            if cart_item.item.quantity < cart_item.quantity:
                raise ValueError(
                    f"Недостаточно товара '{cart_item.item.name}' на складе. "
                    f"Доступно: {cart_item.item.quantity}, запрошено: {cart_item.quantity}"
                )
        
        # Рассчитываем общую сумму
        total_amount = sum(
            cart_item.item.price * cart_item.quantity 
            for cart_item in cart_items
        )
        
        # Создаем заказ
        order = await self.db.orders.add_order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address,
            contact_phone=order_data.contact_phone,
            notes=order_data.notes
        )
        
        # Создаем позиции заказа
        for cart_item in cart_items:
            await self.db.order_items.add_order_item(
                order_id=order.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.item.price
            )
            
            # Уменьшаем остаток товара
            await self.db.items.update_quantity(
                cart_item.item_id, 
                -cart_item.quantity
            )
        
        # Очищаем корзину
        await self.db.cart_items.delete(user_id=user_id)
        
        await self.db.commit()
        return order.id
    
    async def get_user_orders(self, user_id: int, page: int = 1, per_page: int = 10):
        """Получение заказов пользователя с пагинацией"""
        offset = (page - 1) * per_page
        
        orders = await self.db.orders.get_user_orders(
            user_id=user_id,
            limit=per_page,
            offset=offset
        )
        
        total = await self.db.orders.count_user_orders(user_id)
        
        return {
            "orders": orders,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    
    async def get_order(self, user_id: int, order_id: int) -> OrderGet | None:
        """Получение детальной информации о заказе"""
        order = await self.db.orders.get_order_with_items(user_id, order_id)
        return order
    
    async def cancel_order(self, user_id: int, order_id: int):
        """Отмена заказа"""
        order = await self.db.orders.get_one_or_none(id=order_id, user_id=user_id)
        
        if not order:
            raise ObjectNotFoundError("Заказ не найден")
        
        if order.status not in ["pending", "processing"]:
            raise ValueError("Невозможно отменить заказ в текущем статусе")
        
        # Возвращаем товары на склад
        order_items = await self.db.order_items.get_by_order(order_id)
        for order_item in order_items:
            await self.db.items.update_quantity(
                order_item.item_id,
                order_item.quantity
            )
        
        # Обновляем статус заказа
        await self.db.orders.update_status(order_id, "cancelled")
        await self.db.commit()