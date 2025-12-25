from typing import List
from app.exceptions.base import ObjectNotFoundError
from app.schemes.reviews import ReviewGet
from app.services.base import BaseService


class ReviewsService(BaseService):
    
    async def create_review(self, user_id: int, review_data):
        """Создание отзыва о товаре"""
        # Проверяем существование товара
        item = await self.db.items.get_one_or_none(id=review_data.item_id)
        if not item:
            raise ObjectNotFoundError("Товар не найден")
        
        # Проверяем, покупал ли пользователь этот товар
        has_purchased = await self.db.orders.has_user_purchased_item(user_id, review_data.item_id)
        
        if not has_purchased:
            raise ValueError("Вы можете оставить отзыв только на купленные товары")
        
        # Проверяем, не оставлял ли уже пользователь отзыв на этот товар
        existing_review = await self.db.reviews.get_one_or_none(
            user_id=user_id,
            item_id=review_data.item_id
        )
        
        if existing_review:
            raise ValueError("Вы уже оставляли отзыв на этот товар")
        
        # Создаем отзыв
        review = await self.db.reviews.add_review(
            user_id=user_id,
            item_id=review_data.item_id,
            rating=review_data.rating,
            description=review_data.description
        )
        
        await self.db.commit()
        return review
    
    async def get_item_reviews(self, item_id: int, page: int = 1, per_page: int = 10):
        """Получение отзывов на товар"""
        offset = (page - 1) * per_page
        
        reviews = await self.db.reviews.get_item_reviews(
            item_id=item_id,
            limit=per_page,
            offset=offset
        )
        
        total = await self.db.reviews.count_item_reviews(item_id)
        
        # Получаем средний рейтинг
        avg_rating = await self.db.reviews.get_average_rating(item_id)
        
        return {
            "reviews": reviews,
            "average_rating": avg_rating,
            "total_reviews": total,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    
    async def update_review(self, user_id: int, review_id: int, review_data):
        """Обновление отзыва"""
        review = await self.db.reviews.get_one_or_none(
            id=review_id,
            user_id=user_id
        )
        
        if not review:
            raise ObjectNotFoundError("Отзыв не найден")
        
        await self.db.reviews.edit(
            review_data,
            id=review_id,
            user_id=user_id
        )
        
        await self.db.commit()
    
    async def delete_review(self, user_id: int, review_id: int):
        """Удаление отзыва"""
        review = await self.db.reviews.get_one_or_none(
            id=review_id,
            user_id=user_id
        )
        
        if not review:
            raise ObjectNotFoundError("Отзыв не найден")
        
        await self.db.reviews.delete(id=review_id, user_id=user_id)
        await self.db.commit()
    
    async def moderate_review(self, review_id: int, status: str):
        """Модерация отзыва (для администраторов)"""
        review = await self.db.reviews.get_one_or_none(id=review_id)
        
        if not review:
            raise ObjectNotFoundError("Отзыв не найден")
        
        await self.db.reviews.update_status(review_id, status)
        await self.db.commit()