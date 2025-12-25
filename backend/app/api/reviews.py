from fastapi import APIRouter, HTTPException
from typing import Optional

from app.api.dependencies import DBDep, UserIdDep, PaginationDep
from app.exceptions.base import ObjectNotFoundError
from app.schemes.reviews import ReviewCreate, ReviewUpdate, ReviewGet
from app.services.reviews import ReviewsService

router = APIRouter(prefix="/reviews", tags=["Отзывы"])


@router.get("/items/{item_id}", summary="Получение отзывов на товар")
async def get_item_reviews(
    db: DBDep,
    item_id: int,
    pagination: PaginationDep = None,
) -> dict:
    try:
        return await ReviewsService(db).get_item_reviews(
            item_id,
            page=pagination.page,
            per_page=pagination.per_page
        )
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail="Товар не найден")


@router.post("/", summary="Создание отзыва")
async def create_review(
    db: DBDep,
    user_id: UserIdDep,
    review_data: ReviewCreate,
) -> dict[str, str]:
    try:
        await ReviewsService(db).create_review(user_id, review_data)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "OK"}


@router.put("/{review_id}", summary="Обновление отзыва")
async def update_review(
    db: DBDep,
    user_id: UserIdDep,
    review_id: int,
    review_data: ReviewUpdate,
) -> dict[str, str]:
    try:
        await ReviewsService(db).update_review(user_id, review_id, review_data)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}


@router.delete("/{review_id}", summary="Удаление отзыва")
async def delete_review(
    db: DBDep,
    user_id: UserIdDep,
    review_id: int,
) -> dict[str, str]:
    try:
        await ReviewsService(db).delete_review(user_id, review_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}


@router.patch("/{review_id}/moderate", summary="Модерация отзыва (для администраторов)")
async def moderate_review(
    db: DBDep,
    user_id: UserIdDep,
    review_id: int,
    status: str,
) -> dict[str, str]:
    # Проверяем, что пользователь является администратором
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if not user or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await ReviewsService(db).moderate_review(review_id, status)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}