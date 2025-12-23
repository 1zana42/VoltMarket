from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.cart import CartItemModel
from app.repositories.base import BaseRepository


class CartItemsRepository(BaseRepository):
    model = CartItemModel
    schema = None  # Используется только через сервисы

    async def get_user_cart(self, user_id: int):
        """Получение корзины пользователя с информацией о товарах"""
        query = (
            select(self.model)
            .options(selectinload(self.model.item))
            .filter_by(user_id=user_id)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_cart_item(self, user_id: int, cart_item_data):
        """Добавление товара в корзину"""
        cart_item = {
            "user_id": user_id,
            "item_id": cart_item_data.item_id,
            "quantity": cart_item_data.quantity
        }
        
        return await self.add(cart_item)

    async def update_quantity(self, user_id: int, item_id: int, quantity: int):
        """Обновление количества товара в корзине"""
        await self.edit(
            {"quantity": quantity},
            user_id=user_id,
            item_id=item_id
        )

    async def delete(self, user_id: int = None, item_id: int = None, **kwargs):
        """Удаление товаров из корзины"""
        delete_stmt = delete(self.model)
        
        if user_id:
            delete_stmt = delete_stmt.where(self.model.user_id == user_id)
        
        if item_id:
            delete_stmt = delete_stmt.where(self.model.item_id == item_id)
        
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                delete_stmt = delete_stmt.where(getattr(self.model, key) == value)
        
        await self.session.execute(delete_stmt)