import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.items import router as items_router
from app.api.categories import router as categories_router
from app.api.cart import router as cart_router
from app.api.orders import router as orders_router
from app.api.comparisons import router as comparisons_router
from app.api.reviews import router as reviews_router

app = FastAPI(
    title="VoltMarket - Интернет-магазин электроники",
    version="1.0.0",
    description="API для интернет-магазина электроники VoltMarket",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(items_router)
app.include_router(categories_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(comparisons_router)
app.include_router(reviews_router)


@app.get("/", summary="Главная страница API")
async def root():
    return {
        "message": "Добро пожаловать в VoltMarket API!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)