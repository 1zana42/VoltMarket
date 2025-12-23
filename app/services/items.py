from app.exceptions.base import ObjectNotFoundError
from app.schemes.items import ItemCreate, ItemUpdate, ItemSearchParams
from app.services.base import BaseService


class ItemsService(BaseService):
    
    async def create_item(self, item_data: ItemCreate):
        """Создание нового товара"""
        # Проверяем существование категории и бренда
        category = await self.db.categories.get_one_or_none(id=item_data.category_id)
        if not category:
            raise ObjectNotFoundError("Категория не найдена")
            
        brand = await self.db.brands.get_one_or_none(id=item_data.brand_id)
        if not brand:
            raise ObjectNotFoundError("Бренд не найден")
            
        # Проверяем уникальность SKU
        existing_item = await self.db.items.get_one_or_none(sku=item_data.sku)
        if existing_item:
            raise ObjectAlreadyExistsError("Товар с таким артикулом уже существует")
            
        new_item = await self.db.items.add(item_data)
        await self.db.commit()
        return new_item

    async def get_item(self, item_id: int):
        """Получение товара с детальной информацией"""
        item = await self.db.items.get_with_relations(item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
        return item

    async def update_item(self, item_id: int, item_data: ItemUpdate):
        """Обновление товара"""
        item = await self.db.items.get_one_or_none(id=item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
            
        await self.db.items.edit(item_data, id=item_id)
        await self.db.commit()

    async def delete_item(self, item_id: int):
        """Удаление товара"""
        item = await self.db.items.get_one_or_none(id=item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
            
        await self.db.items.delete(id=item_id)
        await self.db.commit()

    async def search_items(self, search_params: ItemSearchParams, page: int = 1, per_page: int = 20):
        """Поиск и фильтрация товаров"""
        offset = (page - 1) * per_page
        filters = search_params.model_dump(exclude_none=True)
        
        items = await self.db.items.search_items(filters, limit=per_page, offset=offset)
        total_count = await self._count_items(filters)
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        }

    async def update_stock(self, item_id: int, quantity_change: int):
        """Обновление остатков товара (продавец может управлять остатками)"""
        try:
            item = await self.db.items.update_quantity(item_id, quantity_change)
            if not item:
                raise ObjectNotFoundError("Товар не найден")
            return item
        except ValueError as e:
            raise ValueError(str(e))

    async def