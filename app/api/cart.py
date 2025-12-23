from fastapi import APIRouter

from app.api.dependencies import DBDep, UserIdDep
from app.schemes.cart import CartItemAdd, CartItemUpdate, CartGet
from app.services.cart import CartService

router = APIRouter(prefix="/cart", tags=["Корзина"])


@router.get("/", summary="Получение содержимого корзины")
async def get_cart(
    db: DBDep,
    user_id: UserIdDep,
) -> CartGet:
    return await CartService(db).get_cart(user_id)


@router.post("/items", summary="Добавление товара в корзину")
async def add_to_cart(
    db: DBDep,
    user_id: UserIdDep,
    cart_item: CartItemAdd,
) -> dict[str, str]:
    try:
        await CartService(db).add_item(user_id, cart_item)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail="Товар не найден")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "OK"}


@router.put("/items/{item_id}", summary="Обновление количества товара в корзине")
async def update_cart_item(
    db: DBDep,
    user_id: UserIdDep,
    item_id: int,
    cart_item: CartItemUpdate,
) -> dict[str, str]:
    try:
        await CartService(db).update_item(user_id, item_id, cart_item.quantity)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    
    return {"status": "OK"}


@router.delete("/items/{item_id}", summary="Удаление товара из корзины")
async def remove_from_cart(
    db: DBDep,
    user_id: UserIdDep,
    item_id: int,
) -> dict[str, str]:
    try:
        await CartService(db).remove_item(user_id, item_id)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    
    return {"status": "OK"}


@router.delete("/", summary="Очистка корзины")
async def clear_cart(
    db: DBDep,
    user_id: UserIdDep,
) -> dict[str, str]:
    await CartService(db).clear_cart(user_id)
    return {"status": "OK"}