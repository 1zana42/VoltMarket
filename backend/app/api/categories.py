from fastapi import APIRouter

from app.api.dependencies import DBDep
from app.exceptions.base import ObjectNotFoundError, ObjectNotFoundHTTPError
from app.schemes.categories import CategoryCreate, CategoryUpdate, CategoryGetWithChildren
from app.services.categories import CategoriesService

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("/", summary="Получение дерева категорий")
async def get_categories_tree(
    db: DBDep,
) -> list[CategoryGetWithChildren]:
    return await CategoriesService(db).get_tree()


@router.get("/{category_id}", summary="Получение информации о категории")
async def get_category(
    db: DBDep,
    category_id: int,
) -> CategoryGetWithChildren:
    try:
        return await CategoriesService(db).get_category_with_children(category_id)
    except ObjectNotFoundError:
        raise ObjectNotFoundHTTPError


@router.post("/", summary="Создание новой категории")
async def create_category(
    db: DBDep,
    category_data: CategoryCreate,
) -> dict[str, str]:
    try:
        await CategoriesService(db).create_category(category_data)
    except ObjectAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Категория с таким названием уже существует")
    
    return {"status": "OK"}


@router.put("/{category_id}", summary="Обновление категории")
async def update_category(
    db: DBDep,
    category_id: int,
    category_data: CategoryUpdate,
) -> dict[str, str]:
    try:
        await CategoriesService(db).update_category(category_id, category_data)
    except ObjectNotFoundError:
        raise ObjectNotFoundHTTPError
    
    return {"status": "OK"}