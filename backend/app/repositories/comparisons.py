from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.comparisons import ComparisonModel, ComparisonItemModel
from app.repositories.base import BaseRepository
from app.schemes.comparisons import ComparisonGet, ComparisonItemGet


class ComparisonsRepository(BaseRepository):
    model = ComparisonModel
    schema = ComparisonGet

    async def get_user_comparisons(self, user_id: int):
        """Получение сравнений пользователя"""
        query = (
            select(self.model)
            .options(selectinload(self.model.items).selectinload(ComparisonItemModel.item))
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
        )
        
        result = await self.session.execute(query)
        comparisons = result.scalars().all()
        
        return [self.schema.model_validate(comp, from_attributes=True) for comp in comparisons]

    async def add_comparison(self, user_id: int, name: str):
        """Создание нового сравнения"""
        comparison_data = {
            "user_id": user_id,
            "name": name
        }
        
        return await self.add(comparison_data)

    async def get_one_or_none_with_items(self, **filter_by):
        """Получение сравнения с товарами"""
        query = (
            select(self.model)
            .options(selectinload(self.model.items).selectinload(ComparisonItemModel.item))
            .filter_by(**filter_by)
        )
        
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        
        if model is None:
            return None
        
        return self.schema.model_validate(model, from_attributes=True)


class ComparisonItemsRepository(BaseRepository):
    model = ComparisonItemModel
    schema = ComparisonItemGet

    async def add_item(self, comparison_id: int, item_id: int):
        """Добавление товара в сравнение"""
        comparison_item = {
            "comparison_id": comparison_id,
            "item_id": item_id
        }
        
        return await self.add(comparison_item)

    async def count_by_comparison(self, comparison_id: int) -> int:
        """Подсчет количества товаров в сравнении"""
        query = select(func.count(self.model.id)).filter_by(comparison_id=comparison_id)
        result = await self.session.execute(query)
        return result.scalar() or 0