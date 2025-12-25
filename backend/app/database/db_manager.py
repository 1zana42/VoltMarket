from app.database.database import async_session_maker
from app.repositories.roles import RolesRepository
from app.repositories.users import UsersRepository
from app.repositories.items import ItemsRepository
from app.repositories.categories import CategoriesRepository
from app.repositories.brands import BrandsRepository
from app.repositories.orders import OrdersRepository
from app.repositories.order_items import OrderItemsRepository
from app.repositories.cart_items import CartItemsRepository
from app.repositories.comparisons import ComparisonsRepository, ComparisonItemsRepository
from app.repositories.reviews import ReviewsRepository


class DBManager:
    def __init__(self, session_factory: async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        
        # Подключаем все репозитории
        self.users = UsersRepository(self.session)
        self.roles = RolesRepository(self.session)
        self.items = ItemsRepository(self.session)
        self.categories = CategoriesRepository(self.session)
        self.brands = BrandsRepository(self.session)
        self.orders = OrdersRepository(self.session)
        self.order_items = OrderItemsRepository(self.session)
        self.cart_items = CartItemsRepository(self.session)
        self.comparisons = ComparisonsRepository(self.session)
        self.comparison_items = ComparisonItemsRepository(self.session)
        self.reviews = ReviewsRepository(self.session)
        
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()