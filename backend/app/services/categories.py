from app.exceptions.base import ObjectNotFoundError, ObjectAlreadyExistsError
from app.schemes.categories import CategoryGetWithChildren
from app.services.base import BaseService


class CategoriesService(BaseService):
    
    async def create_category(self, category_data):
        """Создание новой категории"""
        # Проверяем уникальность имени
        existing_category = await self.db.categories.get_one_or_none(
            name=category_data.name
        )
        
        if existing_category:
            raise ObjectAlreadyExistsError("Категория с таким названием уже существует")
        
        # Если указан родитель, проверяем его существование
        if category_data.parent_id:
            parent_category = await self.db.categories.get_one_or_none(
                id=category_data.parent_id
            )
            
            if not parent_category:
                raise ObjectNotFoundError("Родительская категория не найдена")
        
        # Создаем категорию
        await self.db.categories.add(category_data)
        await self.db.commit()
    
    async def get_category_with_children(self, category_id: int) -> CategoryGetWithChildren:
        """Получение категории с дочерними категориями"""
        category = await self.db.categories.get_with_children(category_id)
        
        if not category:
            raise ObjectNotFoundError("Категория не найдена")
        
        return category
    
    async def get_tree(self):
        """Получение дерева категорий"""
        return await self.db.categories.get_tree()
    
    async def update_category(self, category_id: int, category_data):
        """Обновление категории"""
        category = await self.db.categories.get_one_or_none(id=category_id)
        
        if not category:
            raise ObjectNotFoundError("Категория не найдена")
        
        # Провярем, не пытаемся ли сделать категорию родителем самой себе
        if category_data.parent_id == category_id:
            raise ValueError("Категория не может быть родителем самой себе")
        
        # Если указан родитель, проверяем его существование
        if category_data.parent_id:
            parent_category = await self.db.categories.get_one_or_none(
                id=category_data.parent_id
            )
            
            if not parent_category:
                raise ObjectNotFoundError("Родительская категория не найдена")
        
        await self.db.categories.edit(category_data, id=category_id)
        await self.db.commit()