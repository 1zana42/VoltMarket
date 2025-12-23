from fastapi import APIRouter

from app.api.dependencies import DBDep, UserIdDep
from app.schemes.comparisons import ComparisonCreate, ComparisonItemAdd, ComparisonGet
from app.services.comparisons import ComparisonsService

router = APIRouter(prefix="/comparisons", tags=["Сравнение товаров"])


@router.get("/", summary="Получение списка сравнений")
async def get_comparisons(
    db: DBDep,
    user_id: UserIdDep,
) -> list[ComparisonGet]:
    return await ComparisonsService(db).get_user_comparisons(user_id)


@router.post("/", summary="Создание нового сравнения")
async def create_comparison(
    db: DBDep,
    user_id: UserIdDep,
    comparison_data: ComparisonCreate,
) -> dict[str, str]:
    comparison_id = await ComparisonsService(db).create_comparison(user_id, comparison_data)
    return {"status": "OK", "comparison_id": comparison_id}


@router.post("/{comparison_id}/items", summary="Добавление товара в сравнение")
async def add_to_comparison(
    db: DBDep,
    user_id: UserIdDep,
    comparison_id: int,
    item_data: ComparisonItemAdd,
) -> dict[str, str]:
    try:
        await ComparisonsService(db).add_item_to_comparison(user_id, comparison_id, item_data.item_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "OK"}


@router.delete("/{comparison_id}/items/{item_id}", summary="Удаление товара из сравнения")
async def remove_from_comparison(
    db: DBDep,
    user_id: UserIdDep,
    comparison_id: int,
    item_id: int,
) -> dict[str, str]:
    try:
        await ComparisonsService(db).remove_item_from_comparison(user_id, comparison_id, item_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "OK"}


@router.get("/{comparison_id}", summary="Получение сравнения с детальной информацией")
async def get_comparison_details(
    db: DBDep,
    user_id: UserIdDep,
    comparison_id: int,
) -> dict:
    try:
        return await ComparisonsService(db).get_comparison_details(user_id, comparison_id)
    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))