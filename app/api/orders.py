from fastapi import APIRouter

from app.api.dependencies import DBDep, UserIdDep, PaginationDep
from app.schemes.orders import OrderCreate, OrderGet
from app.services.orders import OrdersService

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.get("/", summary="Получение списка заказов пользователя")
async def get_orders(
    db: DBDep,
    user_id: UserIdDep,
    pagination: PaginationDep = None,
) -> dict:
    return await OrdersService(db).get_user_orders(
        user_id, 
        page=pagination.page, 
        per_page=pagination.per_page
    )


@router.post("/", summary="Создание нового заказа")
async def create_order(
    db: DBDep,
    user_id: UserIdDep,
    order_data: OrderCreate,
) -> dict[str, str]:
    try:
        order_id = await OrdersService(db).create_order(user_id, order_data)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "OK", "order_id": order_id}


@router.get("/{order_id}", summary="Получение информации о заказе")
async def get_order(
    db: DBDep,
    user_id: UserIdDep,
    order_id: int,
) -> OrderGet:
    order = await OrdersService(db).get_order(user_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order