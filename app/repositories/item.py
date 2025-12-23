from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload

from app.models.items import ItemModel
from app.models.reviews import ReviewModel
from app.repositories.base import BaseRepository
from app.schemes.items import ItemGet, ItemGetWithRelations


class ItemsRepository(BaseRepository):
    model = ItemModel
    schema = ItemGet

    async def get_with_relations(self, item_id: int) -> ItemGetWithRelations | None:
        query = (
            select(self.model)
            .options(
                selectinload(self.model.category),
                selectinload(self.model.brand),
                selectinload(self.model.specifications).joinedload("specification_type"),
            )
            .filter_by(id=item_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        
        if model is None:
            return None
            
        # Вычисляем средний рейтинг
        rating_query = select(func.avg(ReviewModel.rating)).where(ReviewModel.item_id == item_id)
        rating_result = await self.session.execute(rating_query)
        average_rating = rating_result.scalar()
        
        # Получаем количество отзывов
        count_query = select(func.count(ReviewModel.id)).where(ReviewModel.item_id == item_id)
        count_result = await self.session.execute(count_query)
        review_count = count_result.scalar()
        
        item_data = ItemGetWithRelations.model_validate(model, from_attributes=True)
        item_data.average_rating = float(average_rating) if average_rating else None
        item_data.review_count = review_count or 0
        
        return item_data

    async def search_items(self, filters: dict, limit: int = 20, offset: int = 0):
        query = select(self.model).options(
            selectinload(self.model.category),
            selectinload(self.model.brand),
        )
        
        # Применяем фильтры
        if filters.get("name"):
            query = query.filter(self.model.name.ilike(f"%{filters['name']}%"))
        if filters.get("category_id"):
            query = query.filter_by(category_id=filters["category_id"])
        if filters.get("brand_id"):
            query = query.filter_by(brand_id=filters["brand_id"])
        if filters.get("min_price"):
            query = query.filter(self.model.price >= filters["min_price"])
        if filters.get("max_price"):
            query = query.filter(self.model.price <= filters["max_price"])
        if filters.get("in_stock"):
            query = query.filter(self.model.quantity > 0)
            
        # Сортировка
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")
        
        if sort_by == "price":
            order_column = self.model.price
        elif sort_by == "name":
            order_column = self.model.name
        elif sort_by == "rating":
            # Здесь нужен подзапрос для рейтинга
            rating_subq = (
                select(ReviewModel.item_id, func.avg(ReviewModel.rating).label('avg_rating'))
                .group_by(ReviewModel.item_id)
                .subquery()
            )
            query = query.outerjoin(rating_subq, self.model.id == rating_subq.c.item_id)
            order_column = func.coalesce(rating_subq.c.avg_rating, 0)
        else:  # created_at
            order_column = self.model.created_at
            
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
            
        # Пагинация
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        return [ItemGetWithRelations.model_validate(item, from_attributes=True) for item in items]

    async def update_quantity(self, item_id: int, quantity_change: int):
        query = select(self.model).filter_by(id=item_id)
        result = await self.session.execute(query)
        item = result.scalars().one_or_none()
        
        if item:
            new_quantity = item.quantity + quantity_change
            if new_quantity < 0:
                raise ValueError("Недостаточно товара на складе")
                
            item.quantity = new_quantity
            await self.session.commit()
            
        return item