from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.reviews import ReviewModel
from app.models.users import UserModel
from app.repositories.base import BaseRepository
from app.schemes.reviews import ReviewGet


class ReviewsRepository(BaseRepository):
    model = ReviewModel
    schema = ReviewGet

    async def add_review(self, user_id: int, item_id: int, rating: int, description: str):
        """Создание нового отзыва"""
        review_data = {
            "user_id": user_id,
            "item_id": item_id,
            "rating": rating,
            "description": description,
            "status": "pending"
        }
        
        return await self.add(review_data)

    async def get_item_reviews(self, item_id: int, limit: int = 10, offset: int = 0):
        """Получение отзывов на товар"""
        query = (
            select(self.model)
            .options(selectinload(self.model.user))
            .filter_by(item_id=item_id, status="approved")
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        reviews = result.scalars().all()
        
        reviews_data = []
        for review in reviews:
            review_data = self.schema.model_validate(review, from_attributes=True)
            review_data.user_name = review.user.name
            reviews_data.append(review_data)
        
        return reviews_data

    async def count_item_reviews(self, item_id: int) -> int:
        """Подсчет количества отзывов на товар"""
        query = select(func.count(self.model.id)).filter_by(item_id=item_id, status="approved")
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_average_rating(self, item_id: int) -> float:
        """Получение среднего рейтинга товара"""
        query = select(func.avg(self.model.rating)).filter_by(item_id=item_id, status="approved")
        result = await self.session.execute(query)
        avg_rating = result.scalar()
        return float(avg_rating) if avg_rating else 0.0

    async def update_status(self, review_id: int, status: str):
        """Обновление статуса отзыва"""
        await self.edit({"status": status}, id=review_id)