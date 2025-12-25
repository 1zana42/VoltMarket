from fastapi import APIRouter, Query
from typing import Optional

from app.api.dependencies import DBDep, UserIdDep, PaginationDep
from app.exceptions.base import ObjectNotFoundError, ObjectNotFoundHTTPError
from app.schemes.items import (
    ItemCreate, 
    ItemUpdate, 
    ItemGetWithRelations,
    ItemSearchParams
)
from app.services.items import ItemsService

router = APIRouter(prefix="/items", tags=["Товары"])


@router.get("/", summary="Поиск и фильтрация товаров")
async def search_items(
    db: DBDep,
    name: Optional[str] = Query(None, description="Название товара"),
    category_id: Optional[int] = Query(None, description="ID категории"),
    brand_id: Optional[int] = Query(None, description="ID бренда"),
    min_price: Optional[int] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[int] = Query(None, ge=0, description="Максимальная цена"),
    in_stock: Optional[bool] = Query(None, description="В наличии"),
    sort_by: Optional[str] = Query("created_at", description="Сортировка по"),
    sort_order: Optional[str] = Query("desc", description="Порядок сортировки"),
    pagination: PaginationDep = None,
) -> dict:
    search_params = ItemSearchParams(
        name=name,
        category_id=category_id,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    result = await ItemsService(db).search_items(
        search_params,
        page=pagination.page,
        per_page=pagination.per_page
    )
    return result


@router.get("/{item_id}", summary="Получение информации о товаре")
async def get_item(
    db: DBDep,
    item_id: int,
) -> ItemGetWithRelations:
    try:
        return await ItemsService(db).get_item(item_id)
    except ObjectNotFoundError:
        raise ObjectNotFoundHTTPError


@router.post("/", summary="Создание нового товара (для продавца)")
async def create_item(
    db: DBDep,
    user_id: UserIdDep,
    item_data: ItemCreate,
) -> dict[str, str]:
    # Проверяем, что пользователь является продавцом
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if not user or user.role.name != "seller":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await ItemsService(db).create_item(item_data)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ObjectAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    return {"status": "OK"}


@router.put("/{item_id}", summary="Обновление товара (для продавца)")
async def update_item(
    db: DBDep,
    user_id: UserIdDep,
    item_id: int,
    item_data: ItemUpdate,
) -> dict[str, str]:
    # Проверяем, что пользователь является продавцом
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if not user or user.role.name != "seller":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await ItemsService(db).update_item(item_id, item_data)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}


@router.delete("/{item_id}", summary="Удаление товара (для продавца)")
async def delete_item(
    db: DBDep,
    user_id: UserIdDep,
    item_id: int,
) -> dict[str, str]:
    # Проверяем, что пользователь является продавцом
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if not user or user.role.name != "seller":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await ItemsService(db).delete_item(item_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}


@router.patch("/{item_id}/stock", summary="Обновление остатков товара")
async def update_stock(
    db: DBDep,
    user_id: UserIdDep,
    item_id: int,
    quantity_change: int = Query(..., description="Изменение количества (+/-)"),
) -> dict[str, str]:
    # Проверяем, что пользователь является продавцом
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if not user or user.role.name != "seller":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await ItemsService(db).update_stock(item_id, quantity_change)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "OK"}