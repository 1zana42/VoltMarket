from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.categories import CategoryModel
from app.models.items import ItemModel
from app.repositories.base import BaseRepository
from app.schemes.categories import CategoryGet, CategoryGetWithChildren


class CategoriesRepository(BaseRepository):
    model = CategoryModel
    schema = CategoryGet

    async def get_with_children(self, category_id: int) -> CategoryGetWithChildren | None:
        query = (
            select(self.model)
            .options(selectinload(self.model.children))
            .filter_by(id=category_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        
        if model is None:
            return None
            
        # Считаем количество товаров в категории
        count_query = select(func.count(ItemModel.id)).where(ItemModel.category_id == category_id)
        count_result = await self.session.execute(count_query)
        item_count = count_result.scalar() or 0
        
        category_data = CategoryGetWithChildren.model_validate(model, from_attributes=True)
        category_data.item_count = item_count
        
        return category_data

    async def get_tree(self):
        query = (
            select(self.model)
            .options(selectinload(self.model.children))
            .filter_by(parent_id=None)
        )
        
        result = await self.session.execute(query)
        categories = result.scalars().all()
        
        return [CategoryGetWithChildren.model_validate(cat, from_attributes=True) for cat in categories]