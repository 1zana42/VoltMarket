from app.exceptions.base import ObjectNotFoundError
from app.schemes.cart import CartGet, CartItemGet
from app.services.base import BaseService


class CartService(BaseService):
    
    async def get_cart(self, user_id: int) -> CartGet:
        """Получение корзины пользователя"""
        cart_items = await self.db.cart_items.get_user_cart(user_id)
        
        total_items = 0
        total_amount = 0
        items_data = []
        
        for item in cart_items:
            total_items += item.quantity
            item_total = item.quantity * item.item.price
            total_amount += item_total
            
            items_data.append(CartItemGet(
                id=item.id,
                item_id=item.item.id,
                item_name=item.item.name,
                item_price=item.item.price,
                item_image_url=item.item.main_image_url,
                quantity=item.quantity,
                total_price=item_total
            ))
        
        return CartGet(
            items=items_data,
            total_items=total_items,
            total_amount=total_amount
        )
    
    async def add_item(self, user_id: int, cart_item_data):
        """Добавление товара в корзину"""
        # Проверяем существование товара
        item = await self.db.items.get_one_or_none(id=cart_item_data.item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
        
        # Проверяем наличие на складе
        if item.quantity < cart_item_data.quantity:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {item.quantity}")
        
        # Проверяем, есть ли уже товар в корзине
        existing_item = await self.db.cart_items.get_one_or_none(
            user_id=user_id, 
            item_id=cart_item_data.item_id
        )
        
        if existing_item:
            # Обновляем количество
            new_quantity = existing_item.quantity + cart_item_data.quantity
            await self.db.cart_items.update_quantity(
                user_id=user_id, 
                item_id=cart_item_data.item_id, 
                quantity=new_quantity
            )
        else:
            # Добавляем новый товар
            await self.db.cart_items.add_cart_item(user_id, cart_item_data)
        
        await self.db.commit()
    
    async def update_item(self, user_id: int, item_id: int, quantity: int):
        """Обновление количества товара в корзине"""
        if quantity <= 0:
            await self.remove_item(user_id, item_id)
            return
        
        # Проверяем наличие товара на складе
        item = await self.db.items.get_one_or_none(id=item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
        
        if item.quantity < quantity:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {item.quantity}")
        
        cart_item = await self.db.cart_items.get_one_or_none(
            user_id=user_id, 
            item_id=item_id
        )
        
        if not cart_item:
            raise ObjectNotFoundError("Товар не найден в корзине")
        
        await self.db.cart_items.update_quantity(user_id, item_id, quantity)
        await self.db.commit()
    
    async def remove_item(self, user_id: int, item_id: int):
        """Удаление товара из корзины"""
        cart_item = await self.db.cart_items.get_one_or_none(
            user_id=user_id, 
            item_id=item_id
        )
        
        if not cart_item:
            raise ObjectNotFoundError("Товар не найден в корзине")
        
        await self.db.cart_items.delete(user_id=user_id, item_id=item_id)
        await self.db.commit()
    
    async def clear_cart(self, user_id: int):
        """Очистка корзины"""
        await self.db.cart_items.delete(user_id=user_id)
        await self.db.commit()